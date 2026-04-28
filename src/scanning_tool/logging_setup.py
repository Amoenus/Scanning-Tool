"""Logger configuration for the scanning tool using loguru."""

from __future__ import annotations

import logging
import sys
from types import FrameType
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from flask import Flask
    from loguru import Logger

LOG_FILE_NAME = "scanning_tool.log"
INTERCEPT_LOGGERS: Sequence[str] = ("werkzeug", "flask.app", "flask")


class InterceptHandler(logging.Handler):
    """Route standard library logging records into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: int | str = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        if (
            record.name == "httpx"
            and record.levelno == logging.INFO
            and record.getMessage().startswith("HTTP Request:")
        ):
            level = "DEBUG"

        logger.opt(depth=_calculate_frame_depth(), exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def _calculate_frame_depth() -> int:
    frame: FrameType | None = logging.currentframe()
    depth = 2
    while frame is not None and frame.f_code.co_filename == __file__:
        frame = frame.f_back
        depth += 1
    return depth


def _apply_intercept_handler(logger_name: str) -> None:
    intercepted_logger = logging.getLogger(logger_name)
    intercepted_logger.handlers = [InterceptHandler()]
    intercepted_logger.propagate = False


def setup_logging() -> Logger:
    """Configure loguru logger with console and file handlers."""
    logger.remove()

    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>"
        ":<cyan>{line}</cyan> - <level>{message}</level>"
    )
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    )

    logger.add(
        sys.stdout,
        level="INFO",
        format=console_format,
        colorize=True,
    )
    logger.add(
        LOG_FILE_NAME,
        rotation="10 MB",
        retention=5,
        level="INFO",
        encoding="utf-8",
        format=file_format,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for logger_name in INTERCEPT_LOGGERS:
        _apply_intercept_handler(logger_name)
    return logger


def configure_flask_logging(app: Flask) -> None:
    """Attach Flask and Werkzeug loggers to the loguru handler."""
    app.logger.handlers = [InterceptHandler()]
    app.logger.propagate = False
    for logger_name in INTERCEPT_LOGGERS:
        _apply_intercept_handler(logger_name)
