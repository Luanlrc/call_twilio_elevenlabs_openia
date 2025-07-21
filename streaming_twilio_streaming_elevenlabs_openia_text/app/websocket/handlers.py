import json
import time
import asyncio
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from config import SHOW_TIMING_MATH
from services.elevenlabs_service import ElevenLabsService
from services.openai_service import OpenAIService
from services.twilio_service import TwilioService
from utils.logger import log_info, log_error, log_debug

class WebSocketHandler:
    def __init__(self):
        self.stream_sid = None
        self.latest_media_timestamp = 0
        self.last_assistant_item = None
        self.mark_queue = []
        self.response_start_timestamp_twilio = None
        self.user_speaking = False
        self.last_speech_event_time = 0
        self.speech_debounce_delay = 1.0

    async def receive_from_twilio(self, websocket: WebSocket, openai_ws):
        """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
        try:
            async for message in websocket.iter_text():
                data = json.loads(message)
                log_debug("📨", f"Evento recebido do Twilio: {data['event']}")
                
                if TwilioService.is_media_event(data) and openai_ws.open:
                    self.latest_media_timestamp = TwilioService.process_media_timestamp(data)
                    await OpenAIService.send_audio_append(openai_ws, data['media']['payload'])
                    log_debug("🎤", f"Áudio recebido do Twilio (timestamp: {self.latest_media_timestamp}ms)")
                
                elif TwilioService.is_start_event(data):
                    self.stream_sid = TwilioService.get_stream_sid(data)
                    log_info("📞", f"Stream iniciado: {self.stream_sid}")
                    self.response_start_timestamp_twilio = None
                    self.latest_media_timestamp = 0
                    self.last_assistant_item = None
                
                elif TwilioService.is_mark_event(data):
                    if self.mark_queue:
                        self.mark_queue.pop(0)
                        log_debug("✅", "Mark processado")
                
                elif TwilioService.is_stop_event(data):
                    log_info("🛑", "Stream parado")
                
                elif TwilioService.is_error_event(data):
                    log_error("❌", f"Erro no stream Twilio: {data}")
        
        except WebSocketDisconnect:
            log_info("🔌", "Cliente desconectado")
            if openai_ws.open:
                await openai_ws.close()
        except Exception as e:
            log_error("💥", f"Erro em receive_from_twilio: {e}")

    async def send_to_twilio(self, websocket: WebSocket, openai_ws):
        """Receive events from the OpenAI Realtime API, send audio back to Twilio using ElevenLabs Streaming."""
        buffer_texto = ""

        try:
            async for openai_message in openai_ws:
                response = json.loads(openai_message)
                current_time = time.time()

                if response['type'] == 'session.created':
                    log_info("🎭", "Sessão OpenAI criada")
                
                elif response['type'] == 'response.create':
                    if 'input' in response and 'content' in response['input']:
                        for content in response['input']['content']:
                            if content.get('type') == 'text' and 'text' in content:
                                log_info("👤", f"Usuário disse: '{content['text']}'")
        
                elif response['type'] == 'input_audio_buffer.speech_started':
                    if not self.user_speaking and (current_time - self.last_speech_event_time) > self.speech_debounce_delay:
                        self.user_speaking = True
                        self.last_speech_event_time = current_time
                        log_info("🎤", "Cliente começou a falar")
                
                elif response['type'] == 'input_audio_buffer.speech_stopped':
                    if self.user_speaking:
                        self.user_speaking = False
                        self.last_speech_event_time = current_time
                        log_info("🔇", "Cliente parou de falar")
                
                elif response['type'] == 'input_audio_buffer.committed':
                    if not self.user_speaking and (current_time - self.last_speech_event_time) < 2.0:
                        log_info("📝", "Áudio do cliente processado")
                
                elif response['type'] == 'rate_limits.updated':
                    remaining = response.get('rate_limits', [{}])[0].get('remaining', 'N/A')
                    log_debug("⚡", f"Rate limits atualizados - Restante: {remaining}")
                
                elif response['type'] == 'error':
                    log_error("❌", f"Erro da API OpenAI: {response}")

                if response.get('type') == 'response.text.delta':
                    buffer_texto += response.get('delta', "")

                elif response.get('type') == 'response.done':
                    if response.get('response', {}).get('output'):
                        for output_item in response['response']['output']:
                            if output_item.get('content'):
                                for content in output_item['content']:
                                    if content.get('type') == 'audio' and content.get('transcript'):
                                        buffer_texto = content['transcript']
                                        break
                    
                    if buffer_texto:
                        log_info("💬", f"IA responde: '{buffer_texto}'")
                        await ElevenLabsService.stream_audio_to_twilio(buffer_texto, websocket, self.stream_sid)

                        if self.response_start_timestamp_twilio is None:
                            self.response_start_timestamp_twilio = self.latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                log_debug("⏱️", f"Timestamp inicial definido: {self.response_start_timestamp_twilio}ms")

                        if response.get('item_id'):
                            self.last_assistant_item = response['item_id']

                        await TwilioService.send_mark(websocket, self.stream_sid, self.mark_queue)
                        log_info("✅", "Áudio da IA enviado!")
                        buffer_texto = ""

                elif response.get('type') == 'input_audio_buffer.speech_started':
                    if self.last_assistant_item and self.user_speaking:
                        log_info("🔄", f"Cliente interrompeu a IA (ID: {self.last_assistant_item})")
                        await self.handle_speech_started_event(websocket, openai_ws)

        except Exception as e:
            log_error("💥", f"Erro em send_to_twilio: {e}")

    async def handle_speech_started_event(self, websocket: WebSocket, openai_ws):
        """Handle interruption when the caller's speech starts."""
        log_info("🔄", "Processando interrupção de fala")
        if self.mark_queue and self.response_start_timestamp_twilio is not None:
            elapsed_time = self.latest_media_timestamp - self.response_start_timestamp_twilio
            if SHOW_TIMING_MATH:
                log_debug("⏱️", f"Tempo decorrido para truncamento: {elapsed_time}ms")

            if self.last_assistant_item:
                if SHOW_TIMING_MATH:
                    log_debug("✂️", f"Truncando item ID: {self.last_assistant_item}")

                await OpenAIService.send_truncate_event(openai_ws, self.last_assistant_item, elapsed_time)
                await TwilioService.send_clear_event(websocket, self.stream_sid)

                self.mark_queue.clear()
                self.last_assistant_item = None
                self.response_start_timestamp_twilio = None
                log_info("🧹", "Estado limpo após interrupção")

    async def handle_connection(self, websocket: WebSocket, openai_ws):
        """Handle the main WebSocket communication."""
        await asyncio.gather(
            self.receive_from_twilio(websocket, openai_ws),
            self.send_to_twilio(websocket, openai_ws)
        )