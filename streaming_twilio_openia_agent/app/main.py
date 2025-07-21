from websocket.manager import WebSocketManager
from fastapi import FastAPI, WebSocket
from routes import call_routes
from config import settings

app = FastAPI()

app.include_router(call_routes.router)

ws_manager = WebSocketManager()

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    client_protocols = websocket.headers.get('sec-websocket-protocol', '')
    if client_protocols:
        await websocket.accept(subprotocol='twilio-streaming')
    else:
        await websocket.accept()
    
    await ws_manager.handle_connection(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)