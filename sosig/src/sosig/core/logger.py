import logging

from rich.logging import RichHandler

from .config import settings


def get_logger(name: str, debug: bool = None):
    """
    Configure and get a logger with the given name.
    Uses settings from config if debug not explicitly provided.
    """
    debug = settings.logging.DEBUG if debug is None else debug
    log_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    rich_handler = RichHandler(rich_tracebacks=True)
    rich_handler.setLevel(log_level)

    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(rich_handler)

    return logger


log = get_logger(__name__)
