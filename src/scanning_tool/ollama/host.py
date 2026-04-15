import os
from typing import Tuple
from urllib.parse import urlparse

from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config


def sanitize_ollama_host(value: str) -> str:
    """Return a normalized Ollama host string, adding http:// when missing."""
    host = (value or "").strip()
    if not host:
        return ""
    if not service_state.host_scheme_re.match(host):
        host = f"http://{host}"
    return host


def get_ollama_host() -> str:
    """Return the configured Ollama host, preferring environment config."""
    env_host = os.getenv("OLLAMA_HOST", "").strip()
    if env_host:
        return sanitize_ollama_host(env_host)
    if config.ollama_config.host:
        return config.ollama_config.host
    return config.ollama_config.default_host


def set_configured_ollama_model(value: str) -> str:
    """Update the configured Ollama model and persist it to the config."""
    sanitized = (value or "").strip()
    if sanitized:
        if sanitized != config.ollama_config.model:
            config.ollama_config.model = sanitized
            os.environ["OLLAMA_MODEL"] = sanitized
            save_config()
    else:
        config.ollama_config.model = ""
        os.environ.pop("OLLAMA_MODEL", None)
        save_config()
    return sanitized


def set_configured_ollama_host(value: str) -> str:
    """Update the configured Ollama host and refresh environment state."""
    sanitized = sanitize_ollama_host(value)
    if sanitized != config.ollama_config.host:
        config.ollama_config.host = sanitized
        if sanitized:
            os.environ["OLLAMA_HOST"] = sanitized
        else:
            os.environ.pop("OLLAMA_HOST", None)
    return sanitized


def get_ollama_model() -> str:
    """Return the active Ollama model, preferring environment config."""
    env_model = os.getenv("OLLAMA_MODEL", "").strip()
    return env_model or config.ollama_config.model


def _normalize_for_parse(host: str) -> str:
    return host if "://" in host else f"http://{host}"


def is_local_ollama_host(host: str) -> bool:
    """Return whether the host string refers to a local Ollama host."""
    try:
        parsed = urlparse(_normalize_for_parse(host))
    except Exception:
        return True
    hostname = (parsed.hostname or "").strip().lower()
    if not hostname or hostname in {"localhost", "0.0.0.0", "127.0.0.1", "::1"}:
        return True
    if hostname.startswith("127."):
        return True
    return False


def _get_host_port(host: str) -> Tuple[str, int]:
    """Return hostname and port for the given Ollama host string."""
    parsed = urlparse(_normalize_for_parse(host))
    hostname = parsed.hostname or "127.0.0.1"
    port = parsed.port or 11434
    return hostname, port
