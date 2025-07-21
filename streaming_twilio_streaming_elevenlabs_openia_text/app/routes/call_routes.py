from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Connect

router = APIRouter()

@router.get("/", response_class=JSONResponse)
async def index_page():
    """Rota inicial que confirma que o servidor está rodando."""
    return {"message": "Twilio Media Stream Server is running!"}

@router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    response.say("Please wait while we connect your call to the A. I. voice assistant, powered by Twilio and the Open-A.I. Realtime API")
    response.pause(length=1)
    response.say("O.K. you can start talking!")
    host = request.url.hostname
    connect = Connect()
    # Configuração ajustada para melhor qualidade de áudio
    connect.stream(
        url=f'wss://{host}/media-stream',
        track='inbound_track',  # Captura apenas áudio do usuário
        max_duration=60,  # Aumentado para 60 segundos
        max_connections=1
    )
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")