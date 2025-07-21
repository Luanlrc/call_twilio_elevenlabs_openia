import os
from twilio.rest import Client
from utils.logger import log_info, log_error
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)

class TwilioService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    async def create_call(self, to_number: str, from_number: str, webhook_url: str):
        return self.client.calls.create(
            to=to_number,
            from_=from_number,
            url=webhook_url
        )

    @staticmethod
    def process_media_event(data: dict) -> bool:
        """Verifica se o evento é um evento de mídia."""
        return data['event'] == 'media'

    @staticmethod
    def process_start_event(data: dict) -> str:
        """
        Processa evento de início e retorna o stream_sid.
        
        Args:
            data: Dados do evento
        Returns:
            str: Stream SID
        """
        return data['start']['streamSid']

    @staticmethod
    def process_stop_event(data: dict) -> bool:
        """Verifica se o evento é um evento de parada."""
        return data['event'] == 'stop'

    @staticmethod
    async def send_media_event(websocket, stream_sid: str, payload: str):
        """
        Envia evento de mídia para o Twilio.
        
        Args:
            websocket: Conexão WebSocket ativa
            stream_sid: ID da stream
            payload: Payload de áudio
        """
        try:
            await websocket.send_json({
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": payload
                }
            })
        except Exception as e:
            log_error("❌", f"Erro ao enviar evento de mídia: {e}")
            raise

    @staticmethod
    async def send_mark_event(websocket, stream_sid: str):
        """
        Envia evento de marcação para o Twilio.
        
        Args:
            websocket: Conexão WebSocket ativa
            stream_sid: ID da stream
        """
        try:
            await websocket.send_json({
                "event": "mark",
                "streamSid": stream_sid,
                "mark": {
                    "name": "audio_streaming"
                }
            })
        except Exception as e:
            log_error("❌", f"Erro ao enviar marca: {e}")
            raise

    @staticmethod
    async def send_clear_event(websocket, stream_sid: str):
        """
        Envia evento de limpeza para o Twilio.
        
        Args:
            websocket: Conexão WebSocket ativa
            stream_sid: ID da stream
        """
        try:
            await websocket.send_json({
                "event": "clear",
                "streamSid": stream_sid
            })
        except Exception as e:
            log_error("❌", f"Erro ao enviar evento clear: {e}")
            raise

    @staticmethod
    def validate_event(data: dict) -> bool:
        """
        Valida se o evento recebido é válido.
        
        Args:
            data: Dados do evento
        Returns:
            bool: True se o evento é válido
        """
        return (
            isinstance(data, dict) and
            'event' in data and
            data['event'] in ['media', 'start', 'stop', 'mark']
        )

    @staticmethod
    def get_event_type(data: dict) -> str:
        """
        Retorna o tipo do evento.
        
        Args:
            data: Dados do evento
        Returns:
            str: Tipo do evento
        """
        return data.get('event', '')