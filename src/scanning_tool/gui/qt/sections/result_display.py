"""Result display section for the Qt scanning tool GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFormLayout, QGroupBox, QSpinBox, QVBoxLayout, QWidget

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action

if TYPE_CHECKING:
    from scanning_tool.gui.qt.sections.base import SectionContext


class ResultDisplaySection:
    """Display offset controls for the on-screen label overlay."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx
        group = QGroupBox("Result Display", parent)
        layout = QVBoxLayout(group)
        form = QFormLayout()

        self._offset_x = self._create_spinbox(ctx.config.overlay_config.info_offset.x)
        self._offset_y = self._create_spinbox(ctx.config.overlay_config.info_offset.y)

        form.addRow("Display offset X", self._offset_x)
        form.addRow("Display offset Y", self._offset_y)
        layout.addLayout(form)

        self._offset_x.valueChanged.connect(self._on_offset_change)
        self._offset_y.valueChanged.connect(self._on_offset_change)

        return group

    def _create_spinbox(self, value: int) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setRange(-800, 800)
        spinbox.setValue(value)
        return spinbox

    def _on_offset_change(self, _: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_RESULT_DISPLAY_OFFSET,
            {"x": self._offset_x.value(), "y": self._offset_y.value()},
        )
