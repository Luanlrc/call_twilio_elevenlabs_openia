import json
from config import (
    logger, log_info, log_debug, 
    VOICE, SYSTEM_MESSAGE
)

class OpenAIService:
    @staticmethod
    async def initialize_session(openai_ws):
        """Control initial session with OpenAI."""
        log_info("⚙️", "Inicializando sessão OpenAI...")
        session_update = {
            "type": "session.update",
            "session": {
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.6,  # Aumenta threshold para reduzir falsos positivos
                    "prefix_padding_ms": 300,  # Padding antes da fala
                    "silence_duration_ms": 500  # Tempo de silêncio para detectar fim da fala
                },
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "voice": VOICE,
                "instructions": SYSTEM_MESSAGE,
                "modalities": ["text", "audio"],
                "temperature": 0.8,
                "model": "gpt-4o",
            }
        }
        log_debug("📋", f"Configuração da sessão: {json.dumps(session_update)}")
        await openai_ws.send(json.dumps(session_update))

    @staticmethod
    async def send_initial_conversation_item(openai_ws):
        """Send initial conversation item if AI talks first."""
        log_info("🎬", "Enviando mensagem inicial da IA")
        initial_conversation_item = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Alo quem fala?"
                    }
                ]
            }
        }
        await openai_ws.send(json.dumps(initial_conversation_item))
        await openai_ws.send(json.dumps({"type": "response.create"}))
        log_info("✅", "Mensagem inicial enviada")

    @staticmethod
    async def send_truncate_event(openai_ws, item_id, elapsed_time):
        """Send truncate event to OpenAI."""
        truncate_event = {
            "type": "conversation.item.truncate",
            "item_id": item_id,
            "content_index": 0,
            "audio_end_ms": elapsed_time
        }
        await openai_ws.send(json.dumps(truncate_event))

    @staticmethod
    async def send_audio_append(openai_ws, audio_payload):
        """Send audio append event to OpenAI."""
        audio_append = {
            "type": "input_audio_buffer.append",
            "audio": audio_payload
        }
        await openai_ws.send(json.dumps(audio_append))