import base64
import audioop
import numpy as np
from io import BytesIO
from pydub import AudioSegment
from utils.logger import log_info, log_error

def convert_ulaw_to_pcm(ulaw_audio_base64: str) -> AudioSegment:
    """
    Converte áudio G711 μ-law base64 para PCM.
    
    Args:
        ulaw_audio_base64: String base64 contendo áudio μ-law
    
    Returns:
        AudioSegment: Áudio convertido para PCM
    """
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
        
        return audio
        
    except Exception as e:
        log_error("❌", f"Erro na conversão ulaw->pcm: {e}")
        return None

def convert_elevenlabs_to_ulaw(audio_data: bytes) -> str:
    """
    Converte áudio do Elevenlabs para G711 μ-law.
    
    Args:
        audio_data: Bytes do áudio do ElevenLabs
    
    Returns:
        str: String base64 contendo áudio μ-law
    """
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
        
        # Converte para 8kHz (taxa do Twilio)
        audio = audio.set_frame_rate(8000)
        
        # Converte para μ-law
        pcm_data = audio.raw_data
        ulaw_data = audioop.lin2ulaw(pcm_data, 2)
        
        # Codifica em base64
        return base64.b64encode(ulaw_data).decode('utf-8')

    except Exception as e:
        log_error("❌", f"Erro na conversão para ulaw: {str(e)}")
        return None

def generate_ambient_noise(duration_ms: int) -> str:
    """
    Gera um ruído branco suave para simular ambiente.
    
    Args:
        duration_ms: Duração do ruído em milissegundos
    
    Returns:
        str: String base64 contendo o ruído em formato μ-law
    """
    try:
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
    except Exception as e:
        log_error("❌", f"Erro ao gerar ruído ambiente: {e}")
        return None

def add_room_effect(audio: AudioSegment) -> AudioSegment:
    """
    Adiciona efeito de sala ao áudio.
    
    Args:
        audio: AudioSegment original
    
    Returns:
        AudioSegment: Áudio com efeito de sala
    """
    try:
        # Cria um efeito de eco/reverb
        echo = audio.overlay(audio - 3, position=50)  # -3dB mais baixo, 50ms de delay
        return echo
    except Exception as e:
        log_error("❌", f"Erro ao adicionar efeito de sala: {e}")
        return audio