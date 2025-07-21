from fastapi import WebSocket
from config import logger, log_debug

class TwilioService:
    @staticmethod
    async def send_media_event(websocket: WebSocket, stream_sid: str, audio_payload: str):
        """Send media event to Twilio."""
        await websocket.send_json({
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": audio_payload
            }
        })

    @staticmethod
    async def send_mark(connection: WebSocket, stream_sid: str, mark_queue: list):
        """Send mark event for synchronization."""
        if stream_sid:
            mark_event = {
                "event": "mark",
                "streamSid": stream_sid,
                "mark": {"name": "responsePart"}
            }
            await connection.send_json(mark_event)
            mark_queue.append('responsePart')
            log_debug("📍", "Mark enviado")

    @staticmethod
    async def send_clear_event(websocket: WebSocket, stream_sid: str):
        """Send clear event to Twilio."""
        await websocket.send_json({
            "event": "clear",
            "streamSid": stream_sid
        })

    @staticmethod
    def process_media_timestamp(data: dict) -> int:
        """Process media timestamp from Twilio event."""
        return int(data['media']['timestamp'])

    @staticmethod
    def get_stream_sid(data: dict) -> str:
        """Get stream SID from Twilio start event."""
        return data['start']['streamSid']

    @staticmethod
    def is_media_event(data: dict) -> bool:
        """Check if event is a media event."""
        return data['event'] == 'media'

    @staticmethod
    def is_start_event(data: dict) -> bool:
        """Check if event is a start event."""
        return data['event'] == 'start'

    @staticmethod
    def is_mark_event(data: dict) -> bool:
        """Check if event is a mark event."""
        return data['event'] == 'mark'

    @staticmethod
    def is_stop_event(data: dict) -> bool:
        """Check if event is a stop event."""
        return data['event'] == 'stop'

    @staticmethod
    def is_error_event(data: dict) -> bool:
        """Check if event is an error event."""
        return data['event'] == 'error'