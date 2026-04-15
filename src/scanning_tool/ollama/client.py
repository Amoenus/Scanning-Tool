import ollama
from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config

from .host import get_ollama_host


def reset_ollama_client() -> None:
    """Clear the cached Ollama client so the next call uses the latest host."""
    service_state.ollama_client = None
    service_state.ollama_client_host = ""


def get_ollama_client() -> ollama.Client:
    """Return an Ollama client instance configured for the active host."""
    host = get_ollama_host()
    if service_state.ollama_client is None or service_state.ollama_client_host != host:
        service_state.ollama_client = ollama.Client(host=host)
        service_state.ollama_client_host = host
    return service_state.ollama_client
