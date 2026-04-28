"""Qt controls section for the scanning tool."""
from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.qt.sections.base import SectionContext


class ControlsSection:
    """Capture interval and primary control buttons."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx
        self._root = parent

        container = QGroupBox("Controls", parent)
        layout = QVBoxLayout(container)

        self._interval_spinner = QDoubleSpinBox(container)
        self._interval_spinner.setRange(0.2, 30.0)
        self._interval_spinner.setSingleStep(0.1)
        self._interval_spinner.setValue(ctx.config.continuous_capture_interval)
        self._interval_spinner.valueChanged.connect(self._on_interval_change)

        form_layout = QFormLayout()
        form_layout.addRow("Continuous capture interval (s)", self._interval_spinner)
        layout.addLayout(form_layout)

        button_row = QHBoxLayout()
        self._single_scan_button = QPushButton("Single Scan", container)
        self._single_scan_button.clicked.connect(self._start_single_scan)
        button_row.addWidget(self._single_scan_button)

        self._continuous_button = QPushButton(container)
        self._continuous_button.clicked.connect(self._toggle_continuous_capture)
        button_row.addWidget(self._continuous_button)

        self._save_button = QPushButton("Save Config", container)
        self._save_button.clicked.connect(self._save_config)
        button_row.addWidget(self._save_button)

        layout.addLayout(button_row)

        layout.addWidget(QLabel("Ready", container))

        ctx.scan_state.add_continuous_mode_listener(self._on_continuous_mode_change)
        self._update_continuous_button_text(ctx.scan_state.continuous_mode)

        return container

    def _on_interval_change(self, value: float) -> None:
        publish_ui_action(
            UiActionType.UPDATE_CONTINUOUS_CAPTURE_INTERVAL,
            {"value": float(value)},
        )

    def _start_single_scan(self) -> None:
        publish_ui_action(UiActionType.SINGLE_SCAN)

    def _toggle_continuous_capture(self) -> None:
        publish_ui_action(UiActionType.TOGGLE_CONTINUOUS_CAPTURE)

    def _save_config(self) -> None:
        publish_ui_action(UiActionType.SAVE_CONFIG)

    def _on_continuous_mode_change(self, continuous_mode: bool) -> None:
        QTimer.singleShot(0, lambda: self._update_continuous_button_text(continuous_mode))

    def _update_continuous_button_text(self, continuous_mode: bool) -> None:
        self._continuous_button.setText(
            "Stop Auto Scan" if continuous_mode else "Start Auto Scan",
        )
