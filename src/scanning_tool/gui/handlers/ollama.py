"""Action handlers for ollama."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scanning_tool.gui.handlers.payloads import OllamaHostPayload, OllamaModelPayload
from scanning_tool.ollama import (
    ensure_model_installed,
    get_ollama_host,
    is_local_ollama_host,
    log_model_running_status,
    set_configured_ollama_host,
    set_configured_ollama_model,
)
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.runtime import RuntimeAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.action_context import ActionContext
    from scanning_tool.gui.handlers import Handler


def _handle_apply_ollama_model(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = OllamaModelPayload.model_validate(payload)
    model_value = data.model.strip()
    if not model_value:
        status_updated.send(None, message="Please specify an Ollama model.")
        return

    set_configured_ollama_model(model_value)
    try:
        ensure_model_installed(model_value, exit_on_error=False)
    except Exception as exc:
        status_updated.send(None, message=f"Model install failed: {exc}")
        logging.exception("Failed to install model %s: %s", model_value, exc)
        return

    running = log_model_running_status(model_value)
    message = (
        f"Ollama model set to {model_value} and is currently running."
        if running
        else f"Ollama model set to {model_value}. It is not running yet and will start on first scan."
    )
    status_updated.send(None, message=message)


def _handle_apply_ollama_host(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = OllamaHostPayload.model_validate(payload)
    host_value = data.host.strip()
    normalized = set_configured_ollama_host(host_value)
    context.config.ollama_config.host = normalized
    active_host = get_ollama_host()
    message = (
        f"Remote Ollama host set to {active_host}." if normalized else f"Ollama host cleared. Using {active_host}."
    )
    status_updated.send(None, message=message)


def _handle_use_localhost(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    set_configured_ollama_host("")
    context.config.ollama_config.host = ""
    active_host = get_ollama_host()
    status_updated.send(None, message=f"Ollama host cleared. Using {active_host}.")


def _handle_restart_ollama(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    host = get_ollama_host()
    if not is_local_ollama_host(host):
        status_updated.send(
            None,
            message=(
                "Remote Ollama host configured; local service cannot be restarted. "
                "Switch to localhost to use automatic restart."
            ),
        )
        return

    status_updated.send(None, message="Restarting local Ollama service...")
    try:
        from scanning_tool.services.ollama_service import ollama_service

        if ollama_service.is_running:
            ollama_service.stop()
        ollama_service.start()
    except Exception as exc:
        status_updated.send(None, message=f"Failed to restart local Ollama service: {exc}")
        logging.exception("Failed to restart Ollama service: %s", exc)
    else:
        status_updated.send(None, message="Local Ollama service restarted successfully.")


OLLAMA_ACTION_HANDLERS: dict[object, Handler] = {
    ConfigAction.APPLY_OLLAMA_MODEL: _handle_apply_ollama_model,
    ConfigAction.APPLY_OLLAMA_HOST: _handle_apply_ollama_host,
    ConfigAction.USE_LOCALHOST: _handle_use_localhost,
    RuntimeAction.RESTART_OLLAMA: _handle_restart_ollama,
}
