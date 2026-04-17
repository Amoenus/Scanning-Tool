"""Logger configuration for the scanning tool using loguru."""

from __future__ import annotations

import logging
import sys
from typing import Optional

from flask import Flask
from loguru import logger
from loguru._logger import Logger


class InterceptHandler(logging.Handler):
    """Route standard library logging records into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=_calculate_frame_depth(), exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def _calculate_frame_depth() -> int:
    frame = logging.currentframe()
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
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        "scanning_tool.log",
        rotation="10 MB",
        retention=5,
        level="INFO",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    _apply_intercept_handler("werkzeug")
    _apply_intercept_handler("flask.app")
    return logger


def configure_flask_logging(app: Flask) -> None:
    """Attach Flask and Werkzeug loggers to the loguru handler."""
    app.logger.handlers = [InterceptHandler()]
    app.logger.propagate = False
    _apply_intercept_handler("werkzeug")
