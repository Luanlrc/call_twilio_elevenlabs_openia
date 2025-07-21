import asyncio
import time
from elevenlabs.conversational_ai.conversation import AudioInterface
from fastapi import WebSocket
from utils.audio_utils import convert_ulaw_to_pcm, convert_elevenlabs_to_ulaw
from utils.logger import log_info, log_error

class TwilioAudioInterface(AudioInterface):
    def __init__(self, websocket: WebSocket, stream_sid: str):
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

    async def process_input(self, audio_data: str):
        """Processa áudio recebido do Twilio"""
        if self._running:
            try:
                pcm_audio = convert_ulaw_to_pcm(audio_data)
                if pcm_audio:
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
                    
                    if self.input_callback:
                        self.input_callback(pcm_audio.raw_data)
                    
            except Exception as e:
                log_error("❌", f"Erro no processamento de áudio de entrada: {e}")

    def output(self, audio_data: bytes):
        """Interface síncrona para saída de áudio"""
        if not self._is_interrupted:
            try:
                self.agent_is_speaking = True
                audio_payload = convert_elevenlabs_to_ulaw(audio_data)
                
                if audio_payload:
                    chunk_size = int(8000 * 2 * self._chunk_duration / 1000)
                    chunks = [audio_payload[i:i+chunk_size] for i in range(0, len(audio_payload), chunk_size)]
                    
                    for chunk in chunks:
                        self._run_coroutine(self.websocket.send_json({
                            "event": "media",
                            "streamSid": self.stream_sid,
                            "media": {"payload": chunk}
                        }))
                        time.sleep(self._chunk_duration / 1000)
                    
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