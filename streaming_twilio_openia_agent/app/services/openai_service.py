import json
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    @staticmethod
    async def initialize_session(openai_ws):
        """Control initial session with OpenAI."""
        try:
            logger.info("Inicializando sessão OpenAI...")
            session_update = {
                "type": "session.update",
                "session": {
                    "turn_detection": {"type": "server_vad"},
                    "input_audio_format": "g711_ulaw",
                    "output_audio_format": "g711_ulaw",
                    "voice": settings.VOICE,
                    "instructions": settings.SYSTEM_MESSAGE,
                    "modalities": ["text", "audio"],
                    "temperature": 0.8,
                }
            }
            logger.info(f"Enviando configuração da sessão: {json.dumps(session_update)}")
            await openai_ws.send(json.dumps(session_update))
            logger.info("Sessão OpenAI inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar sessão OpenAI: {e}")
            raise

    @staticmethod
    async def send_initial_conversation_item(openai_ws):
        """Send initial conversation item if AI talks first."""
        initial_conversation_item = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Greet the user with 'Hello there! I am an AI voice assistant powered by Twilio and the OpenAI Realtime API. You can ask me for facts, jokes, or anything you can imagine. How can I help you?'"
                    }
                ]
            }
        }
        await openai_ws.send(json.dumps(initial_conversation_item))
        await openai_ws.send(json.dumps({"type": "response.create"}))