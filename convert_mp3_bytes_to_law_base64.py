from pydub import AudioSegment
import audioop
from io import BytesIO
import base64

def convert_mp3_bytes_to_g711ulaw_base64(mp3_bytes: bytes) -> str:
    """Converte áudio MP3 em bytes para formato G711 µ-law codificado em base64.

    Esta função realiza uma série de conversões de áudio:
    1. Carrega os bytes MP3
    2. Converte para áudio mono com taxa de amostragem de 8kHz
    3. Converte para formato G711 µ-law
    4. Codifica o resultado em base64

    Args:
        mp3_bytes (bytes): Dados do áudio MP3 em formato de bytes.

    Returns:
        str: String codificada em base64 contendo o áudio no formato G711 µ-law.

    Raises:
        ValueError: Se os bytes de entrada não forem um MP3 válido.
        AudioSegmentError: Se houver erro na conversão do áudio.

    Example:
        >>> with open('audio.mp3', 'rb') as f:
        ...     mp3_data = f.read()
        >>> ulaw_base64 = convert_mp3_bytes_to_g711ulaw_base64(mp3_data)
    """
    audio = AudioSegment.from_file(BytesIO(mp3_bytes), format="mp3")
    audio = audio.set_channels(1).set_frame_rate(8000).set_sample_width(2)
    pcm_audio = audio.raw_data
    ulaw_audio = audioop.lin2ulaw(pcm_audio, 2)
    return base64.b64encode(ulaw_audio).decode("utf-8")
