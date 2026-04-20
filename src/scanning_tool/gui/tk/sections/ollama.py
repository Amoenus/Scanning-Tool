"""Ollama Connection section — model picker, host entry, and action buttons."""

from __future__ import annotations

from loguru import logger
import webbrowser

import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SectionContext

from ..widgets import (
    create_button_row,
    create_labeled_combobox,
    create_labeled_entry,
    create_status_label,
)
from scanning_tool.ollama import (
    ensure_model_installed,
    get_ollama_host,
    get_ollama_model,
    log_model_running_status,
    set_configured_ollama_host,
    set_configured_ollama_model,
)


def get_local_ip() -> str:
    from scanning_tool.web import get_local_ip as web_get_local_ip

    return web_get_local_ip()


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
        return True, OllamaModelManager._build_activation_message(
            model_value, running
        )

    @staticmethod
    def _build_activation_message(model_value: str, running: bool) -> str:
        if running:
            return (
                f"Ollama model set to {model_value} and is currently running."
            )
        return (
            f"Ollama model set to {model_value}. It is not running yet and will start on first scan."
        )


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
            parent, text="Ollama Connection", style="Glass.TLabelframe"
        )
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status
        self._host_var = tk.StringVar(value=ctx.config.ollama_config.host)
        self._model_var = tk.StringVar(value=ctx.config.ollama_config.model)
        self._active_host_var = tk.StringVar()
        self._active_model_var = tk.StringVar()

        self._build_model_row(frame)
        self._build_host_row(frame, ctx)
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

    def _build_host_row(self, parent: ttk.Widget, ctx: SectionContext) -> None:
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
                ("Open Mobile UI", self._open_mobile_overlay),
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

    def _open_mobile_overlay(self) -> None:
        url = self._build_mobile_overlay_url()

        try:
            webbrowser.open_new_tab(url)
        except Exception as exc:
            self._status.set_status(f"Unable to open browser: {exc}")
            logger.warning("Failed to open mobile overlay URL {}: {}", url, exc)
        else:
            self._status.set_status(f"Opening overlay in browser: {url}")
            logger.info("Opened mobile overlay URL: {}", url)

    def _build_mobile_overlay_url(self) -> str:
        if hasattr(self, "_ctx"):
            web_config = self._ctx.config.web_server_config
        else:
            from scanning_tool.state.manager import config

            web_config = config.web_server_config

        display_host = self._resolve_mobile_overlay_display_host(web_config.host)
        return f"http://{display_host}:{web_config.port}"

    def _resolve_mobile_overlay_display_host(self, host: str) -> str:
        if host == "0.0.0.0":
            return get_local_ip()
        return host if host else "127.0.0.1"
