"""Ollama Connection section — model picker, host entry, and action buttons."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from .base import SectionContext

from scanning_tool.ollama import (
    ensure_model_installed,
    get_ollama_host,
    get_ollama_model,
    is_local_ollama_host,
    log_model_running_status,
    set_configured_ollama_host,
    set_configured_ollama_model,
)
from scanning_tool.services.ollama_service import ollama_service

from ..widgets import (
    create_button_row,
    create_labeled_combobox,
    create_labeled_entry,
    create_status_label,
)


class OllamaModelManager:
    """Encapsulate Ollama model configuration, installation, and status messages."""

    @staticmethod
    def apply_model(model_value: str) -> tuple[bool, str]:
        if not model_value:
            return False, "Please specify an Ollama model."

        set_configured_ollama_model(model_value)
        try:
            ensure_model_installed(model_value, exit_on_error=False)
        except Exception as exc:
            logger.error("Failed to install model {}: {}", model_value, exc)
            return False, f"Model install failed: {exc}"

        running = log_model_running_status(model_value)
        return True, OllamaModelManager._build_activation_message(model_value, running)

    @staticmethod
    def _build_activation_message(model_value: str, running: bool) -> str:
        if running:
            return f"Ollama model set to {model_value} and is currently running."
        return f"Ollama model set to {model_value}. It is not running yet and will start on first scan."


SUGGESTED_MODELS = (
    "moondream:1.8b",
    "granite3.2-vision:2b",
    "deepseek-ocr:3b",
    "smolvlm",
    "bakllava:1.8b",
    "llava:1.5b",
    "qwen2.5vl:3b",
    "qwen3-vl:2b",
    "qwen3-vl:4b",
)


class OllamaSection:
    """Model selector, host entry, and active-status labels for Ollama."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent, text="Ollama Connection", style="Glass.TLabelframe",
        )
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status
        self._host_var = tk.StringVar(value=ctx.config.ollama_config.host)
        self._model_var = tk.StringVar(value=ctx.config.ollama_config.model)
        self._active_host_var = tk.StringVar()
        self._active_model_var = tk.StringVar()

        self._build_model_row(frame)
        self._build_host_row(frame)
        self._build_action_row(frame)
        self._build_active_labels(frame)

        self._refresh_active_labels()
        return frame

    def _build_model_row(self, parent: ttk.Widget) -> None:
        create_labeled_combobox(
            parent,
            text="Ollama model (set in config.json or environment).",
            variable=self._model_var,
            values=list(SUGGESTED_MODELS),
            width=48,
        )

    def _build_host_row(self, parent: ttk.Widget) -> None:
        create_labeled_entry(
            parent,
            text="Remote Ollama host (IPv4/hostname with optional port). Leave blank to use this PC.",
            variable=self._host_var,
        )

    def _build_action_row(self, parent: ttk.Widget) -> None:
        create_button_row(
            parent,
            [
                ("Apply Host", self._apply_host),
                ("Apply Model", self._apply_model),
                ("Use Localhost", self._use_localhost),
                ("Restart Ollama", self._restart_ollama),
            ],
        )

    def _build_active_labels(self, parent: ttk.Widget) -> None:
        create_status_label(parent, self._active_host_var)
        create_status_label(parent, self._active_model_var)

    def _refresh_active_labels(self) -> None:
        self._active_host_var.set(f"Active host: {get_ollama_host()}")
        self._active_model_var.set(f"Active model: {get_ollama_model()}")

    def _apply_model(self) -> None:
        model_value = self._model_var.get().strip()
        success, message = OllamaModelManager.apply_model(model_value)
        if success:
            self._refresh_active_labels()
            logger.info("Ollama model set to {}.", model_value)
        self._status.set_status(message)

    def _apply_host(self) -> None:
        sanitized = set_configured_ollama_host(self._host_var.get())
        self._refresh_active_labels()
        active_host = get_ollama_host()
        if sanitized:
            self._host_var.set(sanitized)
            message = f"Remote Ollama host set to {active_host}."
        else:
            message = f"Ollama host cleared. Using {active_host}."
        self._status.set_status(message)
        logger.info(message)

    def _use_localhost(self) -> None:
        self._host_var.set("")
        set_configured_ollama_host("")
        self._refresh_active_labels()
        message = f"Ollama host cleared. Using {get_ollama_host()}."
        self._status.set_status(message)
        logger.info(message)

    def _restart_ollama(self) -> None:
        host = get_ollama_host()
        if not is_local_ollama_host(host):
            message = (
                "Remote Ollama host configured; local service cannot be restarted. "
                "Switch to localhost to use automatic restart."
            )
            self._status.set_status(message)
            logger.info(message)
            return

        self._status.set_status("Restarting local Ollama service...")
        try:
            if ollama_service.is_running:
                ollama_service.stop()
            ollama_service.start()
        except SystemExit as exc:
            message = f"Failed to restart local Ollama service: {exc}"
            logger.error(message)
        except Exception as exc:
            message = f"Failed to restart local Ollama service: {exc}"
            logger.error(message)
        else:
            message = "Local Ollama service restarted successfully."
            logger.info(message)
        finally:
            self._refresh_active_labels()
            self._status.set_status(message)
