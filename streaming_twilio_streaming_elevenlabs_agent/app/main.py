import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket
from routes import router
from websocket import WebSocketManager
from config import settings, twilio_client  # Importar o cliente aqui
from utils.logger import log_info, log_error

# Inicializa a aplicação FastAPI
app = FastAPI()

# Adiciona as rotas
app.include_router(router)

# Inicializa o WebSocket manager
ws_manager = WebSocketManager()

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and ElevenLabs."""
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
    
    # Faz a ligação ao iniciar
    try:
        # Obtém a URL do ngrok se estiver configurada
        NGROK_URL = os.getenv("NGROK_URL")
        
        if not NGROK_URL:
            print("⚠️  NGROK_URL não configurada. Configure primeiro o ngrok e adicione a URL no .env")
            print("🔄 Iniciando apenas o servidor...")
        else:
            # Usa o cliente Twilio diretamente como no original
            call = twilio_client.calls.create(
                to=settings.CALL_TO_PHONE,
                from_=settings.TWILIO_PHONE_NUMBER,
                url=f"{NGROK_URL}/incoming-call"
            )
            print(f"📞 Iniciando chamada para {settings.CALL_TO_PHONE}")
            print(f"🆔 Call SID: {call.sid}")
    except Exception as e:
        print(f"❌ Erro ao iniciar chamada: {e}")
        print("🔄 Iniciando apenas o servidor...")
    
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)