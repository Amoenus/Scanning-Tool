"""Ollama host, client, service, installer, and model utilities."""

from .client import get_ollama_client, reset_ollama_client
from .host import (
    get_ollama_host,
    get_ollama_model,
    is_local_ollama_host,
    sanitize_ollama_host,
    set_configured_ollama_host,
    set_configured_ollama_model,
)
from .installer import ensure_ollama_installed, show_installation_message
from .models import (
    ensure_model_installed,
    is_model_running,
    list_running_ollama_models,
    log_model_running_status,
)

__all__ = [
    "ensure_model_installed",
    "ensure_ollama_installed",
    "get_ollama_client",
    "get_ollama_host",
    "get_ollama_model",
    "is_local_ollama_host",
    "is_model_running",
    "list_running_ollama_models",
    "log_model_running_status",
    "reset_ollama_client",
    "sanitize_ollama_host",
    "set_configured_ollama_host",
    "set_configured_ollama_model",
    "show_installation_message",
]
