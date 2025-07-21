from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from services.twilio_service import TwilioService
from utils.logger import log_info, log_error
from config import CALL_TO_PHONE, TWILIO_PHONE_NUMBER

router = APIRouter()

@router.get("/", response_class=JSONResponse)
async def index_page():
    """Rota inicial que confirma que o servidor está rodando."""
    return {"message": "Twilio Media Stream Server is running!"}

@router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@router.get("/make-call")
async def make_call(request: Request):
    """Endpoint para iniciar uma chamada"""
    try:
        # Obtém a URL base da aplicação
        base_url = str(request.base_url).rstrip('/')
        
        # Cria a chamada usando o serviço Twilio
        call = await TwilioService.create_call(
            to_number=CALL_TO_PHONE,
            from_number=TWILIO_PHONE_NUMBER,
            webhook_url=f"{base_url}/incoming-call"
        )
        
        log_info("📞", f"Chamada iniciada para {CALL_TO_PHONE}")
        return {"message": "Chamada iniciada", "call_sid": call.sid}
    
    except Exception as e:
        log_error("❌", f"Erro ao iniciar chamada: {e}")
        return {"error": str(e)}, 500