import json
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from services.elevenlabs_service import ElevenLabsService
from services.twilio_service import TwilioService
from utils.logger import log_info, log_error

class WebSocketHandler:
    def __init__(self):
        self.elevenlabs_service = ElevenLabsService()
        self.twilio_service = TwilioService()
        self.stream_sid = None
        self.twilio_interface = None
        self.conversation = None

    async def handle_connection(self, websocket: WebSocket):
        """Handle WebSocket connections between Twilio and ElevenLabs."""
        log_info("👋", "Cliente conectado")

        try:
            async for message in websocket.iter_text():
                data = json.loads(message)
                
                if not self.twilio_service.validate_event(data):
                    log_error("❌", f"Evento inválido recebido: {data}")
                    continue

                event_type = self.twilio_service.get_event_type(data)
                
                if event_type == 'start':
                    await self.handle_start_event(websocket, data)
                elif event_type == 'media':
                    await self.handle_media_event(data)
                elif event_type == 'stop':
                    log_info("🛑", "Chamada finalizada")
                    break
                
        except WebSocketDisconnect:
            log_info("🔌", "Cliente desconectado")
        except Exception as e:
            log_error("💥", f"Erro na conexão: {e}")
        finally:
            await self.cleanup_resources()

    async def handle_start_event(self, websocket: WebSocket, data: dict):
        """Processa evento de início da stream."""
        try:
            self.stream_sid = self.twilio_service.process_start_event(data)
            log_info("📞", f"Stream iniciado: {self.stream_sid}")
            
            # Inicializa conversação ElevenLabs
            self.conversation, self.twilio_interface = await self.elevenlabs_service.create_conversation(
                websocket, 
                self.stream_sid
            )
            
            # Inicia a sessão
            await self.elevenlabs_service.start_conversation(
                self.conversation, 
                self.twilio_interface
            )
            
        except Exception as e:
            log_error("❌", f"Erro ao iniciar sessão: {e}")
            if self.twilio_interface:
                self.twilio_interface.stop()
            raise

    async def handle_media_event(self, data: dict):
        """Processa evento de mídia."""
        try:
            if self.twilio_interface and self.conversation:
                audio_payload = data['media']['payload']
                await self.elevenlabs_service.process_audio_input(
                    self.twilio_interface, 
                    audio_payload
                )
        except Exception as e:
            log_error("❌", f"Erro ao processar áudio: {e}")

    async def cleanup_resources(self):
        """Limpa recursos ao finalizar conexão."""
        try:
            if self.twilio_interface:
                self.twilio_interface.stop()
            
            if self.conversation:
                await self.elevenlabs_service.end_conversation(
                    self.conversation, 
                    self.twilio_interface
                )
            
            log_info("🧹", "Recursos limpos com sucesso")
            
        except Exception as e:
            log_error("❌", f"Erro ao limpar recursos: {e}")