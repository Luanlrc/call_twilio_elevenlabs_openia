import asyncio
from elevenlabs import ElevenLabs
from elevenlabs.client import ElevenLabs
import os
from config import logger, log_info, log_error, ELEVENLABS_VOICE_ID
from utils.audio_utils import convert_mp3_bytes_to_g711ulaw_base64

# Configuração do ElevenLabs
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

class ElevenLabsService:
    @staticmethod
    async def stream_audio_to_twilio(texto, websocket, stream_sid, voz_escolhida=ELEVENLABS_VOICE_ID):
        """Stream audio directly from ElevenLabs to Twilio using real streaming"""
        try:
            log_info("🎵", "Iniciando streaming real de áudio com ElevenLabs...")
            
            audio_stream = elevenlabs.text_to_speech.stream(
                text=texto,
                voice_id=voz_escolhida,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.71,  # Aumentado para mais estabilidade
                    "similarity_boost": 0.75,  # Aumentado para melhor qualidade
                    "style": 0.65,
                    "use_speaker_boost": True
                },
                optimize_streaming_latency=2,  # Reduzido para 2 (era 3)
                output_format="mp3_44100_128"
            )
            
            buffer_chunks = []
            chunk_size = 0
            target_chunk_size = 16384  # Aumentado o tamanho do buffer (era 8192)
            
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    buffer_chunks.append(chunk)
                    chunk_size += len(chunk)
                    
                    # Envia quando atingir o tamanho alvo ou acumular chunks suficientes
                    if chunk_size >= target_chunk_size:
                        combined_chunk = b''.join(buffer_chunks)
                        audio_payload = convert_mp3_bytes_to_g711ulaw_base64(combined_chunk)
                        
                        await websocket.send_json({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": audio_payload}
                        })
                        
                        # Adiciona um pequeno delay para sincronização
                        await asyncio.sleep(0.02)  # 20ms de delay para suavizar a transição
                        
                        buffer_chunks = []
                        chunk_size = 0
            
            # Envia os chunks restantes
            if buffer_chunks:
                combined_chunk = b''.join(buffer_chunks)
                audio_payload = convert_mp3_bytes_to_g711ulaw_base64(combined_chunk)
                await websocket.send_json({
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": audio_payload}
                })
            
            log_info("✅", "Streaming real de áudio concluído!")
            
        except Exception as e:
            log_error("💥", f"Erro no streaming real de áudio: {e}")
            await ElevenLabsService.fallback_audio_generation(texto, websocket, stream_sid, voz_escolhida)

    @staticmethod
    async def fallback_audio_generation(texto, websocket, stream_sid, voz_escolhida=ELEVENLABS_VOICE_ID):
        """Fallback method using traditional ElevenLabs generation"""
        try:
            log_info("🔄", "Usando método tradicional de geração de áudio...")
            
            # Gera o áudio com ElevenLabs usando a nova API
            audio_bytes = elevenlabs.text_to_speech.convert(
                text=texto,
                voice_id=voz_escolhida,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.6,
                    "similarity_boost": 0.65,
                    "style": 0.65,
                    "use_speaker_boost": True
                }
            )

            # Converte MP3 para G711 μ-law base64
            audio_payload = convert_mp3_bytes_to_g711ulaw_base64(audio_bytes)

            # Envia áudio para o Twilio
            await websocket.send_json({
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": audio_payload}
            })
            
            log_info("✅", "Áudio enviado com sucesso (método tradicional)!")
            
        except Exception as e:
            log_error("💥", f"Erro no fallback de áudio: {e}")

    @staticmethod
    def gerar_audio_com_elevenlabs(texto, voz_escolhida=ELEVENLABS_VOICE_ID):
        """Função legada mantida para compatibilidade (usando nova API)"""
        response = elevenlabs.text_to_speech.convert(
            text=texto,
            voice_id=voz_escolhida,
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.6,
                "similarity_boost": 0.65,
                "style": 0.65,
                "use_speaker_boost": True
            }
        )
        return response