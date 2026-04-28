"""Event-driven Ollama status publishing helpers."""

from __future__ import annotations

from loguru import logger

from scanning_tool.state.signals import ollama_readiness_changed, ollama_status_updated


def publish_ollama_status(
    message: str,
    *,
    model: str | None = None,
    host: str | None = None,
    ready: bool | None = None,
) -> None:
    """Publish an Ollama service status event for UI and runtime listeners."""
    logger.info(message)
    ollama_status_updated.send(
        None,
        message=message,
        model=model,
        host=host,
        ready=ready,
    )
    if ready is not None:
        ollama_readiness_changed.send(
            None,
            model=model,
            host=host,
            ready=ready,
        )
