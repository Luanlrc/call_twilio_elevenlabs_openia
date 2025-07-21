import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def log_info(emoji: str, message: str) -> None:
    """Log info message with emoji"""
    logger.info(f"{emoji} {message}")

def log_error(emoji: str, message: str) -> None:
    """Log error message with emoji"""
    logger.error(f"{emoji} {message}")

def log_debug(emoji: str, message: str) -> None:
    """Log debug message with emoji"""
    logger.debug(f"{emoji} {message}")