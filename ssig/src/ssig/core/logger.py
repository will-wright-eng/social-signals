import sys
import logging

from .config import settings


def get_logger(name: str, debug: bool = None):
    """
    Configure and get a logger with the given name.
    Uses settings from config if debug not explicitly provided.
    """
    debug = settings.logging.DEBUG if debug is None else debug

    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Stream handler (console output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)

    formatter = logging.Formatter(settings.logging.LOG_FORMAT)
    stream_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(stream_handler)

    return logger


log = get_logger(__name__)
