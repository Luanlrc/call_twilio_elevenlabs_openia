from fastapi import FastAPI, WebSocket
from routes import call_routes
from websocket.manager import WebSocketManager
from config import PORT, OPENAI_API_KEY

# Verificação da chave API
if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

app = FastAPI()

# Rotas
app.include_router(call_routes.router)

# WebSocket manager
ws_manager = WebSocketManager()

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI with optimized streaming."""
    # Verificar os headers do protocolo WebSocket
    client_protocols = websocket.headers.get('sec-websocket-protocol', '')
    if client_protocols:
        # Aceitar o protocolo do Twilio
        await websocket.accept(subprotocol='twilio-streaming')
    else:
        await websocket.accept()
    
    await ws_manager.handle_connection(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)