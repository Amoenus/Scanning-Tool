"""Service package exports.

This package avoids importing capture service eagerly because that module depends on
runtime state and can create circular imports during application bootstrap.
"""

from scanning_tool.config.service import ConfigService

from .alignment_service import alignment_service
from .ollama_service import ollama_service

config_service = ConfigService()

__all__ = [
    "alignment_service",
    "config_service",
    "ollama_service",
]


def __getattr__(name: str):
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__ + list(globals().keys()))
