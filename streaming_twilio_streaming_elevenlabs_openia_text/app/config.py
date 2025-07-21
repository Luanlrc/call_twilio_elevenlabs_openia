import os
from dotenv import load_dotenv
from prompt import PROMPT
import logging

load_dotenv()

# Configurações
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = PROMPT
VOICE = 'alloy'
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_info(emoji, message):
    logger.info(f"{emoji} {message}")

def log_error(emoji, message):
    logger.error(f"{emoji} {message}")

def log_debug(emoji, message):
    logger.debug(f"{emoji} {message}")