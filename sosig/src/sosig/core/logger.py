import logging

from rich.logging import RichHandler


class Logger:
    def __init__(self, name: str, debug: bool = None):
        """
        Initialize logger with the given name.
        Uses settings from config if debug not explicitly provided.
        """
        self.logger = logging.getLogger(name)
        self.rich_handler = RichHandler(rich_tracebacks=True)

        formatter = logging.Formatter("%(message)s")
        self.rich_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(self.rich_handler)

    def set_debug(self, debug: bool) -> None:
        """Update the logger's debug level"""
        log_level = logging.DEBUG if debug else logging.INFO
        self.logger.setLevel(log_level)
        self.rich_handler.setLevel(log_level)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


log = Logger(__name__)
