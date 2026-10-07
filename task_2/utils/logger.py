"""Application logging configuration."""

import logging
from pathlib import Path


LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIRECTORY / "logs.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Return an application logger that writes INFO events to ``logs/logs.log``."""
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    application_logger = logging.getLogger("voting_app")
    application_logger.setLevel(logging.INFO)
    application_logger.propagate = False

    if not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == LOG_FILE
        for handler in application_logger.handlers
    ):
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        application_logger.addHandler(file_handler)

    return logging.getLogger(f"voting_app.{name}")
