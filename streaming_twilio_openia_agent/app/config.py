import os
from dotenv import load_dotenv
from prompt import PROMPT

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    PORT = int(os.getenv('PORT', 5050))
    SYSTEM_MESSAGE = PROMPT
    VOICE = 'alloy'
    OPENAI_MODEL = 'gpt-4o-realtime-preview-2024-10-01'
    
    LOG_EVENT_TYPES = [
        'error', 'response.content.done', 'rate_limits.updated',
        'response.done', 'input_audio_buffer.committed',
        'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
        'session.created'
    ]

settings = Settings()
