"""Capture Region section for the Qt scanning tool GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.qt.sections.base import SectionContext

if TYPE_CHECKING:
    from scanning_tool.gui.qt.status import StatusBar
    from scanning_tool.gui.qt.status import StatusBar


class CaptureRegionSection:
    """Capture region adjustment controls."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx
        self._status: StatusBar = ctx.status

        group = QGroupBox("Capture Region", parent)
        layout = QVBoxLayout(group)
        form = QFormLayout()

        self._left = self._create_spinbox(ctx.config.capture_region.left)
        self._top = self._create_spinbox(ctx.config.capture_region.top)
        self._width = self._create_spinbox(ctx.config.capture_region.width)
        self._height = self._create_spinbox(ctx.config.capture_region.height)

        form.addRow("Left", self._left)
        form.addRow("Top", self._top)
        form.addRow("Width", self._width)
        form.addRow("Height", self._height)
        layout.addLayout(form)

        self._border_checkbox = QCheckBox("Show capture border", group)
        self._border_checkbox.setChecked(ctx.overlay_state.show_border)
        self._border_checkbox.stateChanged.connect(self._toggle_capture_border)
        ctx.overlay_state.add_show_border_listener(self._on_show_border_visibility_change)
        layout.addWidget(self._border_checkbox)

        self._left.valueChanged.connect(self._on_region_change)
        self._top.valueChanged.connect(self._on_region_change)
        self._width.valueChanged.connect(self._on_region_change)
        self._height.valueChanged.connect(self._on_region_change)

        return group

    def _create_spinbox(self, value: int) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setRange(0, 5000)
        spinbox.setValue(value)
        return spinbox

    def _on_region_change(self, _: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_CAPTURE_REGION,
            {
                "left": self._left.value(),
                "top": self._top.value(),
                "width": self._width.value(),
                "height": self._height.value(),
            },
        )

    def _on_show_border_visibility_change(self, visible: bool) -> None:
        self._border_checkbox.setChecked(visible)

    def _toggle_capture_border(self, state: int) -> None:
        publish_ui_action(
            UiActionType.TOGGLE_CAPTURE_BORDER,
        )
