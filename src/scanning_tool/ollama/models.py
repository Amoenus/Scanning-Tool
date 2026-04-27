from typing import NoReturn

from loguru import logger

from .client import get_ollama_client
from .host import get_ollama_host, get_ollama_model, is_local_ollama_host


class OllamaModelInstaller:
    """Encapsulates Ollama host detection and model installation state."""

    def __init__(self, model: str | None = None, exit_on_error: bool = True) -> None:
        self.model = model or get_ollama_model()
        self.exit_on_error = exit_on_error
        self.host = get_ollama_host()
        self.host_mode = "local" if is_local_ollama_host(self.host) else "remote"
        self.client = get_ollama_client()

    def ensure_installed(self) -> bool:
        if not self.model:
            logger.info(
                "No Ollama model configured. Skipping model installation check.",
            )
            return False

        self._log_host_mode()

        available_models = self._load_available_models()
        if self.model in available_models:
            logger.info(
                f"Model {self.model} already available on Ollama host {self.host}.",
            )
            return True

        return self._pull_model()

    def _log_host_mode(self) -> None:
        logger.info(f"Using {self.host_mode} Ollama host at {self.host}.")

    def _load_available_models(self) -> set[str]:
        try:
            response = self.client.list()
            return {m.model for m in response.models if m.model}
        except Exception as exc:
            self._build_connection_error(exc)

    def _pull_model(self) -> bool:
        logger.info(
            f"Model {self.model} not found on Ollama host {self.host}. Pulling now...",
        )
        try:
            progress = self.client.pull(self.model)
            if progress.status:
                logger.info(f"Ollama pull status: {progress.status}")
            logger.info(f"Model {self.model} installed successfully on {self.host}.")
            return True
        except Exception as exc:
            self._build_installation_error(exc)

    def _build_connection_error(self, exc: Exception) -> NoReturn:
        logger.error(f"Unable to communicate with Ollama at {self.host}: {exc}")
        guidance = (
            "Make sure the Ollama service is running on this PC."
            if self.host_mode == "local"
            else f"Ensure the Ollama server at {self.host} is reachable from this machine."
        )
        if self.exit_on_error:
            raise RuntimeError(guidance) from exc
        raise

    def _build_installation_error(self, exc: Exception) -> NoReturn:
        logger.error(f"Error ensuring model {self.model} on {self.host}: {exc}")
        if self.exit_on_error:
            raise RuntimeError("Failed to ensure Ollama model.") from exc
        raise


def ensure_model_installed(
    model: str | None = None, exit_on_error: bool = True,
) -> bool:
    """Ensure the Ollama model exists on the configured host."""
    return OllamaModelInstaller(
        model=model, exit_on_error=exit_on_error,
    ).ensure_installed()


def list_running_ollama_models() -> list[str]:
    """Return a list of Ollama model names currently running on the active host."""
    client = get_ollama_client()
    try:
        response = client.ps()
        return [m.model for m in response.models if m.model]
    except Exception as e:
        logger.warning("Unable to query Ollama process list: {}", e)
        return []


def is_model_running(model: str | None = None) -> bool:
    """Return whether the given Ollama model is currently running."""
    model = model or get_ollama_model()
    return model in list_running_ollama_models()


def log_model_running_status(model: str | None = None) -> bool:
    """Log the running state of the given Ollama model."""
    model = model or get_ollama_model()
    running_models = list_running_ollama_models()
    if model in running_models:
        logger.info("Ollama model {} is currently running.", model)
        return True
    logger.info(
        "Ollama model {} is not currently running. It will start on first OCR request.",
        model,
    )
    if running_models:
        logger.info("Currently running Ollama models: {}", ", ".join(running_models))
    else:
        logger.info("No Ollama models are currently running.")
    return False
