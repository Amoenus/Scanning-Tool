"""Advanced settings container for the Qt scanning tool GUI."""
from __future__ import annotations

from PyQt6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QWidget

from .base import SectionContext
from .capture_region import CaptureRegionSection
from .head_sway import HeadSwaySection
from .ollama import OllamaSection
from .result_display import ResultDisplaySection


class SettingsSection:
    """Holds advanced configuration sections behind an expandable container."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx

        group = QGroupBox("Advanced Settings", parent)
        layout = QVBoxLayout(group)

        self._toggle_button = QPushButton("Show advanced settings", group)
        self._toggle_button.clicked.connect(self._toggle_visibility)
        layout.addWidget(self._toggle_button)

        self._settings_container = QWidget(group)
        self._settings_layout = QVBoxLayout(self._settings_container)
        self._settings_container.setVisible(False)

        self._settings_layout.addWidget(CaptureRegionSection().build(self._settings_container, ctx))
        self._settings_layout.addWidget(ResultDisplaySection().build(self._settings_container, ctx))
        self._settings_layout.addWidget(OllamaSection().build(self._settings_container, ctx))
        self._settings_layout.addWidget(HeadSwaySection().build(self._settings_container, ctx))

        layout.addWidget(self._settings_container)
        return group

    def _toggle_visibility(self) -> None:
        visible = not self._settings_container.isVisible()
        self._settings_container.setVisible(visible)
        self._toggle_button.setText(
            "Hide advanced settings" if visible else "Show advanced settings",
        )
