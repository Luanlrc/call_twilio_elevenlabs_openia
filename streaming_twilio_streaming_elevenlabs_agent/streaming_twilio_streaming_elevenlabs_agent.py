import os
import json
import base64
import audioop
import asyncio
from pydub import AudioSegment
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import ConversationInitiationData, Conversation, AudioInterface
from prompt import PROMPT
import time

load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = PROMPT

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
CALL_TO_PHONE = "+5541995659361"

# Inicializa o cliente Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Inicializa o cliente ElevenLabs
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Logging configuration
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_info(emoji, message):
    """Log info message with emoji"""
    logger.info(f"{emoji} {message}")

def log_error(emoji, message):
    """Log error message with emoji"""
    logger.error(f"{emoji} {message}")

def log_debug(emoji, message):
    """Log debug message with emoji"""
    logger.debug(f"{emoji} {message}")

def convert_ulaw_to_pcm(ulaw_audio_base64):
    """Converte áudio G711 μ-law base64 para PCM"""
    try:
        # Decodifica o base64
        ulaw_audio = base64.b64decode(ulaw_audio_base64)
        
        # Converte de μ-law para PCM linear 16-bit
        pcm_audio = audioop.ulaw2lin(ulaw_audio, 2)  # 2 bytes por amostra (16-bit)
        
        # Cria um AudioSegment do PCM
        audio = AudioSegment(
            data=pcm_audio,
            sample_width=2,  # 16-bit
            frame_rate=8000,  # 8kHz
            channels=1  # mono
        )
        
        # log_info("🔄", f"Áudio convertido: {len(pcm_audio)} bytes")
        return audio
        
    except Exception as e:
        log_error("❌", f"Erro na conversão ulaw->pcm: {e}")
        return None

def add_room_effect(audio):
    # Cria um efeito de eco/reverb
    echo = audio.overlay(audio - 3, position=50)  # -3dB mais baixo, 50ms de delay
    return echo

def generate_ambient_noise(duration_ms):
    """Gera um ruído branco suave para simular ambiente"""
    import numpy as np
    
    # Gera ruído branco
    sample_rate = 8000
    samples = int((duration_ms / 1000.0) * sample_rate)
    noise = np.random.normal(0, 0.1, samples)
    
    # Converte para bytes
    noise_bytes = (noise * 32767).astype(np.int16).tobytes()
    
    # Converte para μ-law
    ulaw_data = audioop.lin2ulaw(noise_bytes, 2)
    
    # Retorna em base64
    return base64.b64encode(ulaw_data).decode('utf-8')

def convert_elevenlabs_to_ulaw(audio_data):
    """Converte áudio do Elevenlabs para G711 μ-law"""
    try:
        # Carrega o áudio como PCM
        audio = AudioSegment(
            data=audio_data,
            sample_width=2,
            frame_rate=16000,
            channels=1
        )
        
        # Gera ruído do mesmo tamanho do áudio
        noise_base64 = generate_ambient_noise(len(audio))
        noise_bytes = base64.b64decode(noise_base64)
        noise_pcm = audioop.ulaw2lin(noise_bytes, 2)
        
        # Cria AudioSegment do ruído
        noise_audio = AudioSegment(
            data=noise_pcm,
            sample_width=2,
            frame_rate=8000,
            channels=1
        ).set_frame_rate(16000)  # Converte para mesma taxa do áudio
        
        # Reduz volume do ruído
        #noise_audio = noise_audio - 30  # -30dB
        
        # Mixa o áudio com o ruído
        #audio = audio.overlay(noise_audio)
        
        # Converte para 8kHz (taxa do Twilio)
        audio = audio.set_frame_rate(8000)
        
        # Converte para μ-law
        pcm_data = audio.raw_data
        ulaw_data = audioop.lin2ulaw(pcm_data, 2)
        
        # Codifica em base64
        ulaw_base64 = base64.b64encode(ulaw_data).decode('utf-8')
        return ulaw_base64

    except Exception as e:
        log_error("❌", f"Erro na conversão para ulaw: {str(e)}")
        return None

app = FastAPI()

class TwilioAudioInterface(AudioInterface):
    def __init__(self, websocket, stream_sid):
        super().__init__()
        self.websocket = websocket
        self.stream_sid = stream_sid
        self.audio_queue = asyncio.Queue()
        self.should_stop = False
        self.conversation = None
        self.is_speaking = False
        self.agent_is_speaking = False
        self.last_vad_update = 0
        self.speech_timeout = 0.5
        self.input_callback = None
        self._running = False
        self._loop = asyncio.get_event_loop()
        self._is_interrupted = False
        self._session_ended = asyncio.Event()
        self._buffer = []
        self._buffer_size = 0
        self._max_buffer_size = 16384  # 16KB
        self._chunk_duration = 20  # ms por chunk

    def start(self, input_callback):
        """Inicia a interface de áudio"""
        self.input_callback = input_callback
        self._running = True
        self._is_interrupted = False
        self._session_ended.clear()
        log_info("🎙️", "Interface de áudio iniciada")
        return True

    def stop(self):
        """Para a interface de áudio"""
        self._running = False
        self.should_stop = True
        self._session_ended.set()
        log_info("🛑", "Interface de áudio parada")

    def wait_for_session_end(self):
        """Aguarda o fim da sessão"""
        if self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._session_ended.wait(), self._loop)
            return future.result()
        else:
            return self._loop.run_until_complete(self._session_ended.wait())

    def interrupt(self):
        """Interrompe a reprodução de áudio atual"""
        self._is_interrupted = True
        self.agent_is_speaking = False
        self._run_coroutine(self._send_clear_event())
        log_info("⏹️", "Áudio interrompido")

    def _run_coroutine(self, coroutine):
        """Executa uma corotina no loop de eventos"""
        if self._loop.is_running():
            return asyncio.run_coroutine_threadsafe(coroutine, self._loop).result()
        else:
            return self._loop.run_until_complete(coroutine)

    async def process_input(self, audio_data):
        """Processa áudio recebido do Twilio"""
        if self._running:
            try:
                # Converte o áudio de G711 para PCM
                pcm_audio = convert_ulaw_to_pcm(audio_data)
                if pcm_audio:
                    # Detecta atividade de voz
                    current_time = asyncio.get_event_loop().time()
                    rms = pcm_audio.rms
                    is_speech = rms > -30  # Ajuste este valor conforme necessário
                    
                    if is_speech and not self.is_speaking:
                        self.is_speaking = True
                        self.last_vad_update = current_time
                        await self.handle_speech_started()
                    elif is_speech:
                        self.last_vad_update = current_time
                    elif self.is_speaking and (current_time - self.last_vad_update) > self.speech_timeout:
                        self.is_speaking = False
                        await self.handle_speech_stopped()
                    
                    # Envia o áudio para o Elevenlabs
                    if self.input_callback:
                        self.input_callback(pcm_audio.raw_data)
                    
            except Exception as e:
                log_error("❌", f"Erro no processamento de áudio de entrada: {e}")

    def output(self, audio_data):
        """Interface síncrona para saída de áudio"""
        if not self._is_interrupted:
            try:
                self.agent_is_speaking = True
                
                # Converte o áudio para G711 μ-law
                audio_payload = convert_elevenlabs_to_ulaw(audio_data)
                
                if audio_payload:
                    # Envia o áudio para o Twilio em chunks menores
                    chunk_size = int(8000 * 2 * self._chunk_duration / 1000)  # bytes por chunk (8kHz, 16-bit, Xms)
                    chunks = [audio_payload[i:i+chunk_size] for i in range(0, len(audio_payload), chunk_size)]
                    
                    for chunk in chunks:
                        # Envia o chunk
                        self._run_coroutine(self.websocket.send_json({
                            "event": "media",
                            "streamSid": self.stream_sid,
                            "media": {"payload": chunk}
                        }))
                        
                        # Pequena pausa entre chunks
                        time.sleep(self._chunk_duration / 1000)
                    
                    # Envia marca para controle de fluxo
                    self._run_coroutine(self.send_mark())
                    log_info("📤", "Áudio enviado para Twilio")
                else:
                    log_error("❌", "Falha na conversão do áudio")
                    
            except Exception as e:
                log_error("❌", f"Erro ao processar áudio de saída: {e}")
                self.agent_is_speaking = False

    async def handle_speech_started(self):
        """Manipula o início da fala do usuário"""
        log_info("🗣️", "Usuário começou a falar")
        if self.agent_is_speaking:
            self.interrupt()
            log_info("🛑", "Fala do agente interrompida")

    async def handle_speech_stopped(self):
        """Manipula o fim da fala do usuário"""
        self._is_interrupted = False
        log_info("🤫", "Usuário parou de falar")

    async def send_mark(self):
        """Envia marca para controle de fluxo"""
        try:
            await self.websocket.send_json({
                "event": "mark",
                "streamSid": self.stream_sid,
                "mark": {"name": "audio_streaming"}
            })
        except Exception as e:
            log_error("❌", f"Erro ao enviar marca: {e}")

    async def _send_clear_event(self):
        """Envia evento de limpeza para o Twilio"""
        try:
            await self.websocket.send_json({
                "event": "clear",
                "streamSid": self.stream_sid
            })
        except Exception as e:
            log_error("❌", f"Erro ao enviar evento clear: {e}")

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.get("/make-call")
async def make_call(request: Request):
    """Endpoint para iniciar uma chamada"""
    try:
        # Obtém a URL base da aplicação
        base_url = str(request.base_url).rstrip('/')
        
        # Cria a chamada
        call = twilio_client.calls.create(
            to=CALL_TO_PHONE,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{base_url}/incoming-call"
        )
        
        return {"message": "Chamada iniciada", "call_sid": call.sid}
    except Exception as e:
        log_error("❌", f"Erro ao iniciar chamada: {e}")
        return {"error": str(e)}, 500

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and ElevenLabs."""
    print("Cliente conectado")
    await websocket.accept()

    # Estado da conexão
    stream_sid = None
    twilio_interface = None
    conversation = None

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['event'] == 'start':
                stream_sid = data['start']['streamSid']
                log_info("📞", f"Stream iniciado: {stream_sid}")
                
                try:
                    # Inicializa a interface de áudio do Twilio
                    twilio_interface = TwilioAudioInterface(websocket, stream_sid)
                    
                    # Configura e inicia a conversação do Elevenlabs
                    config = ConversationInitiationData()
                    conversation = Conversation(
                        client=client,
                        agent_id=AGENT_ID,
                        requires_auth=True,
                        audio_interface=twilio_interface,
                        config=config,
                        callback_agent_response=lambda response: log_info("🤖", f"Agente: {response}"),
                        callback_user_transcript=lambda transcript: log_info("👤", f"Usuário: {transcript}"),
                        callback_agent_response_correction=lambda original, correction: log_info("📝", f"Correção: {original} -> {correction}")
                    )
                    
                    # Inicia a sessão
                    conversation.start_session()  # Método síncrono, não precisa de await
                    twilio_interface.conversation = conversation
                    log_info("✅", "Sessão iniciada com sucesso")
                    
                except Exception as e:
                    log_error("❌", f"Erro ao iniciar sessão: {e}")
                    if twilio_interface:
                        twilio_interface.stop()
                    raise
                
            elif data['event'] == 'media' and twilio_interface and conversation:
                # Processa o áudio recebido do Twilio
                audio_payload = data['media']['payload']
                await twilio_interface.process_input(audio_payload)
                
            elif data['event'] == 'stop':
                log_info("🛑", "Chamada finalizada")
                break
                
    except WebSocketDisconnect:
        log_info("🔌", "Cliente desconectado")
    except Exception as e:
        log_error("💥", f"Erro na conexão: {e}")
    finally:
        # Limpa recursos
        if twilio_interface:
            twilio_interface.stop()
        if conversation:
            try:
                conversation.end_session()  # Método síncrono, não precisa de await
                twilio_interface.wait_for_session_end()  # Método síncrono
            except Exception as e:
                log_error("❌", f"Erro ao finalizar sessão: {e}")
        log_info("👋", "Conexão encerrada")

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
            # Cria a chamada
            call = twilio_client.calls.create(
                to=CALL_TO_PHONE,
                from_=TWILIO_PHONE_NUMBER,
                url=f"{NGROK_URL}/incoming-call"
            )
            print(f"📞 Iniciando chamada para {CALL_TO_PHONE}")
            print(f"🆔 Call SID: {call.sid}")
    except Exception as e:
        print(f"❌ Erro ao iniciar chamada: {e}")
        print("🔄 Iniciando apenas o servidor...")
    
    # Inicia o servidor
    uvicorn.run(app, host="0.0.0.0", port=PORT) 