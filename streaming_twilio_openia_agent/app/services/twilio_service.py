from fastapi import WebSocket

class TwilioService:
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

    @staticmethod
    async def send_clear_event(websocket: WebSocket, stream_sid: str):
        """Send clear event to Twilio."""
        await websocket.send_json({
            "event": "clear",
            "streamSid": stream_sid
        })