import json
import base64
import asyncio
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from services.twilio_service import TwilioService
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self):
        self.stream_sid = None
        self.latest_media_timestamp = 0
        self.last_assistant_item = None
        self.mark_queue = []
        self.response_start_timestamp_twilio = None

    async def receive_from_twilio(self, websocket: WebSocket, openai_ws):
        """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
        try:
            async for message in websocket.iter_text():
                data = json.loads(message)
                if data['event'] == 'media' and openai_ws.open:
                    self.latest_media_timestamp = int(data['media']['timestamp'])
                    audio_append = {
                        "type": "input_audio_buffer.append",
                        "audio": data['media']['payload']
                    }
                    await openai_ws.send(json.dumps(audio_append))
                elif data['event'] == 'start':
                    self.stream_sid = data['start']['streamSid']
                    print(f"Incoming stream has started {self.stream_sid}")
                    self.response_start_timestamp_twilio = None
                    self.latest_media_timestamp = 0
                    self.last_assistant_item = None
                elif data['event'] == 'mark':
                    if self.mark_queue:
                        self.mark_queue.pop(0)
        except WebSocketDisconnect:
            print("Client disconnected.")
            if openai_ws.open:
                await openai_ws.close()

    async def send_to_twilio(self, websocket: WebSocket, openai_ws):
        """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
        try:
            async for openai_message in openai_ws:
                response = json.loads(openai_message)
                if response['type'] in settings.LOG_EVENT_TYPES:
                    print(f"Received event: {response['type']}", response)

                if response.get('type') == 'response.audio.delta' and 'delta' in response:
                    audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                    audio_delta = {
                        "event": "media",
                        "streamSid": self.stream_sid,
                        "media": {
                            "payload": audio_payload
                        }
                    }
                    await websocket.send_json(audio_delta)

                    if self.response_start_timestamp_twilio is None:
                        self.response_start_timestamp_twilio = self.latest_media_timestamp

                    if response.get('item_id'):
                        self.last_assistant_item = response['item_id']

                    await TwilioService.send_mark(websocket, self.stream_sid, self.mark_queue)

                if response.get('type') == 'input_audio_buffer.speech_started':
                    print("Speech started detected.")
                    if self.last_assistant_item:
                        print(f"Interrupting response with id: {self.last_assistant_item}")
                        await self.handle_speech_started_event(websocket, openai_ws)
        except Exception as e:
            print(f"Error in send_to_twilio: {e}")

    async def handle_speech_started_event(self, websocket: WebSocket, openai_ws):
        """Handle interruption when the caller's speech starts."""
        if self.mark_queue and self.response_start_timestamp_twilio is not None:
            elapsed_time = self.latest_media_timestamp - self.response_start_timestamp_twilio

            if self.last_assistant_item:
                truncate_event = {
                    "type": "conversation.item.truncate",
                    "item_id": self.last_assistant_item,
                    "content_index": 0,
                    "audio_end_ms": elapsed_time
                }
                await openai_ws.send(json.dumps(truncate_event))

            await TwilioService.send_clear_event(websocket, self.stream_sid)
            self.mark_queue.clear()
            self.last_assistant_item = None
            self.response_start_timestamp_twilio = None

    async def handle_connection(self, websocket: WebSocket, openai_ws):
        """Handle the main WebSocket communication."""
        try:
            logger.info("Iniciando manipulação da conexão WebSocket")
            receive_task = asyncio.create_task(
                self.receive_from_twilio(websocket, openai_ws)
            )
            send_task = asyncio.create_task(
                self.send_to_twilio(websocket, openai_ws)
            )
            
            logger.info("Tarefas de envio e recebimento iniciadas")
            
            try:
                await asyncio.gather(receive_task, send_task)
            except asyncio.CancelledError:
                logger.info("Tarefas canceladas")
            except Exception as e:
                logger.error(f"Erro durante a execução das tarefas: {e}")
                raise
        except Exception as e:
            logger.error(f"Erro na manipulação da conexão: {e}")
            if not websocket.client_state.DISCONNECTED:
                await websocket.close()
            raise