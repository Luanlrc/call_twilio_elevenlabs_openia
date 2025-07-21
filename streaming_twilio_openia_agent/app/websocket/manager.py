import websockets
from fastapi import WebSocket
from config import settings
from services.openai_service import OpenAIService
from websocket.handlers import WebSocketHandler
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.handler = WebSocketHandler()

    async def handle_connection(self, websocket: WebSocket):
        """Handle main WebSocket connection."""
        logger.info("Nova conexão WebSocket recebida")
        
        # Conectando com OpenAI exatamente como no original
        openai_ws = await websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
            extra_headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        )

        try:
            logger.info("Iniciando sessão OpenAI...")
            await OpenAIService.initialize_session(openai_ws)
            logger.info("Sessão OpenAI inicializada")
            await self.handler.handle_connection(websocket, openai_ws)
        except Exception as e:
            logger.error(f"Erro na conexão WebSocket: {e}")
            if openai_ws.open:
                await openai_ws.close()
            raise