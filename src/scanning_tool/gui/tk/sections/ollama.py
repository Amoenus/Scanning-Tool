"""Ollama Connection section — model picker, host entry, and action buttons."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.runtime import RuntimeAction

if TYPE_CHECKING:
    from scanning_tool.gui.tk.sections.base import SectionContext

from scanning_tool.gui.tk.widgets import (
    create_button_row,
    create_labeled_combobox,
    create_labeled_entry,
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
    """Model selector, host entry, and action buttons for Ollama."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent, text="Ollama Connection", style="Glass.TLabelframe",
        )
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status
        self._host_var = tk.StringVar(value=ctx.config.ollama_config.host)
        self._model_var = tk.StringVar(value=ctx.config.ollama_config.model)

        self._build_model_row(frame)
        self._build_host_row(frame)
        self._build_action_row(frame)
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

    def _apply_model(self) -> None:
        publish_ui_action(
            ConfigAction.APPLY_OLLAMA_MODEL,
            {"model": self._model_var.get().strip()},
        )

    def _apply_host(self) -> None:
        publish_ui_action(
            ConfigAction.APPLY_OLLAMA_HOST,
            {"host": self._host_var.get().strip()},
        )

    def _use_localhost(self) -> None:
        publish_ui_action(ConfigAction.USE_LOCALHOST)

    def _restart_ollama(self) -> None:
        publish_ui_action(RuntimeAction.RESTART_OLLAMA)

