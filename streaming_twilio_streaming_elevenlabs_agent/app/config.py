import os
from prompt import PROMPT
from twilio.rest import Client

# Configurações do Servidor
PORT = int(os.getenv('PORT', 5050))

# Configurações do Sistema
SYSTEM_MESSAGE = PROMPT

# Configurações do ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY não configurada no .env")

AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
if not AGENT_ID:
    raise ValueError("ELEVENLABS_AGENT_ID não configurado no .env")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Configuração do número de destino
CALL_TO_PHONE = os.getenv("CALL_TO_PHONE")

# Inicializa o cliente Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# Configuração do ngrok (opcional)
NGROK_URL = os.getenv("NGROK_URL")

# Configurações de áudio
AUDIO_CONFIG = {
    'chunk_duration': 20,  # ms por chunk
    'max_buffer_size': 16384,  # 16KB
    'sample_rate': 8000,  # 8kHz
    'channels': 1,  # mono
    'sample_width': 2,  # 16-bit
    'speech_threshold': -30,  # threshold para detecção de voz
    'speech_timeout': 0.5,  # timeout para detecção de fim de fala
}

# Configurações de WebSocket
WEBSOCKET_CONFIG = {
    'ping_interval': 20,  # segundos
    'ping_timeout': 20,  # segundos
    'close_timeout': 20,  # segundos
    'max_message_size': 1024 * 1024,  # 1MB
}

class Settings:
    """Classe para agrupar todas as configurações."""
    
    # Servidor
    PORT = PORT
    
    # Sistema
    SYSTEM_MESSAGE = SYSTEM_MESSAGE
    
    # ElevenLabs
    ELEVENLABS_API_KEY = ELEVENLABS_API_KEY
    AGENT_ID = AGENT_ID
    
    # Twilio
    TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN
    TWILIO_PHONE_NUMBER = TWILIO_PHONE_NUMBER
    CALL_TO_PHONE = CALL_TO_PHONE
    
    # NGROK
    NGROK_URL = NGROK_URL
    
    # Configurações técnicas
    AUDIO_CONFIG = AUDIO_CONFIG
    WEBSOCKET_CONFIG = WEBSOCKET_CONFIG

    @classmethod
    def validate(cls):
        """Valida todas as configurações necessárias."""
        required_vars = [
            'ELEVENLABS_API_KEY',
            'AGENT_ID',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_PHONE_NUMBER'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Variáveis de ambiente não configuradas: {', '.join(missing)}")

# Cria uma instância das configurações
settings = Settings()

# Valida as configurações ao importar
settings.validate()