"""Service package exports.

This package avoids importing capture service eagerly because that module depends on
runtime state and can create circular imports during application bootstrap.
"""

from .alignment_service import alignment_service
from .ollama_service import ollama_service
from scanning_tool.config.service import ConfigService

config_service = ConfigService()

__all__ = [
    "alignment_service",
    "capture_service",
    "config_service",
    "ollama_service",
]


def __getattr__(name: str):
    if name == "capture_service":
        from .capture_service import capture_service

        return capture_service
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__ + list(globals().keys()))
