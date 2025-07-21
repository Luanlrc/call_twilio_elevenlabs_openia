import websockets
from fastapi import WebSocket
from config import OPENAI_API_KEY
from services.openai_service import OpenAIService
from websocket.handlers import WebSocketHandler
from utils.logger import log_info, log_error

class WebSocketManager:
    def __init__(self):
        self.handler = WebSocketHandler()

    async def handle_connection(self, websocket: WebSocket):
        """Handle WebSocket connections between Twilio and OpenAI with optimized streaming."""
        log_info("🔌", "Cliente conectado ao WebSocket")

        try:
            openai_ws = await websockets.connect(
                'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
                extra_headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "OpenAI-Beta": "realtime=v1"
                }
            )

            log_info("", "Conectado à API OpenAI Realtime")
            await OpenAIService.initialize_session(openai_ws)
            await self.handler.handle_connection(websocket, openai_ws)

        except Exception as e:
            log_error("💥", f"Erro na conexão WebSocket: {e}")
            raise