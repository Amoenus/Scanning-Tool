import ollama
from scanning_tool.state import manager

from .host import get_ollama_host


def reset_ollama_client() -> None:
    """Clear the cached Ollama client so the next call uses the latest host."""
    manager.service_state.ollama_client = None
    manager.service_state.ollama_client_host = ""


def get_ollama_client() -> ollama.Client:
    """Return an Ollama client instance configured for the active host."""
    host = get_ollama_host()
    if manager.service_state.ollama_client is None or manager.service_state.ollama_client_host != host:
        manager.service_state.ollama_client = ollama.Client(host=host)
        manager.service_state.ollama_client_host = host
    return manager.service_state.ollama_client
