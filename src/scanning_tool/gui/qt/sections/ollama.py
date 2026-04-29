"""Ollama connection section for the Qt scanning tool GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action

from .base import SectionContext

if TYPE_CHECKING:
    from scanning_tool.gui.qt.status import StatusBar

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

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx
        self._status: StatusBar = ctx.status

        group = QGroupBox("Ollama Connection", parent)
        layout = QVBoxLayout(group)

        form = QFormLayout()
        self._model_combobox = QComboBox(group)
        self._model_combobox.addItems(SUGGESTED_MODELS)
        current_model = ctx.config.ollama_config.model
        if current_model:
            self._model_combobox.setEditText(current_model)
        self._model_combobox.setEditable(True)
        form.addRow("Ollama model", self._model_combobox)

        self._host_input = QLineEdit(ctx.config.ollama_config.host, group)
        form.addRow("Remote Ollama host", self._host_input)

        layout.addLayout(form)
        button_row = QHBoxLayout()

        apply_host = QPushButton("Apply Host", group)
        apply_host.clicked.connect(self._apply_host)
        button_row.addWidget(apply_host)

        apply_model = QPushButton("Apply Model", group)
        apply_model.clicked.connect(self._apply_model)
        button_row.addWidget(apply_model)

        use_local = QPushButton("Use Localhost", group)
        use_local.clicked.connect(self._use_localhost)
        button_row.addWidget(use_local)

        restart = QPushButton("Restart Ollama", group)
        restart.clicked.connect(self._restart_ollama)
        button_row.addWidget(restart)

        layout.addLayout(button_row)
        return group

    def _apply_model(self) -> None:
        model_value = self._model_combobox.currentText().strip()
        publish_ui_action(
            UiActionType.APPLY_OLLAMA_MODEL,
            {"model": model_value},
        )

    def _apply_host(self) -> None:
        host_value = self._host_input.text().strip()
        publish_ui_action(
            UiActionType.APPLY_OLLAMA_HOST,
            {"host": host_value},
        )

    def _use_localhost(self) -> None:
        publish_ui_action(UiActionType.USE_LOCALHOST)

    def _restart_ollama(self) -> None:
        publish_ui_action(UiActionType.RESTART_OLLAMA)
