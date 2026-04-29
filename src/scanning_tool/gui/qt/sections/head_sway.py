"""Head sway compensation section for the Qt scanning tool GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.qt.sections.base import SectionContext

if TYPE_CHECKING:
    from scanning_tool.gui.qt.status import StatusBar


class HeadSwaySection:
    """Anchor tracking and auto-alignment controls."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        """Build and return the head sway compensation section widget.

        Parameters
        ----------
        parent : QWidget
            The parent widget.
        ctx : SectionContext
            The section context containing configuration and state.

        Returns
        -------
        QWidget
            The constructed group box widget for head sway compensation.

        """
        self._ctx = ctx
        self._status: StatusBar = ctx.status

        group = QGroupBox("Head Sway Compensation", parent)
        layout = QVBoxLayout(group)

        self._auto_align_checkbox = QCheckBox("Enable auto alignment", group)
        self._auto_align_checkbox.setChecked(ctx.config.auto_alignment.enabled)
        self._auto_align_checkbox.stateChanged.connect(self._toggle_auto_align)
        layout.addWidget(self._auto_align_checkbox)

        self._anchor_overlay_checkbox = QCheckBox("Show anchor overlay", group)
        self._anchor_overlay_checkbox.setChecked(ctx.overlay_state.anchor_overlay_visible)
        self._anchor_overlay_checkbox.stateChanged.connect(self._toggle_anchor_overlay_visibility)
        ctx.overlay_state.add_anchor_overlay_visibility_listener(
            self._on_anchor_overlay_visibility_change,
        )
        layout.addWidget(self._anchor_overlay_checkbox)

        form = QFormLayout()
        self._interval_spinner = self._create_spinbox(int(ctx.config.alignment_poll_interval_ms), 100, 5000)
        self._threshold_spinner = self._create_spinbox(int(ctx.config.anchor_threshold * 100), 10, 99)
        form.addRow("Alignment interval (ms)", self._interval_spinner)
        form.addRow("Detection threshold (%)", self._threshold_spinner)
        layout.addLayout(form)

        self._interval_spinner.valueChanged.connect(self._update_alignment_interval)
        self._threshold_spinner.valueChanged.connect(self._update_threshold)

        region_form = QFormLayout()
        anchor_region = ctx.config.anchor_template
        anchor_offset = ctx.config.anchor_offset
        self._anchor_left = self._create_spinbox(anchor_region.left, 0, 3840)
        self._anchor_top = self._create_spinbox(anchor_region.top, 0, 2160)
        self._anchor_width = self._create_spinbox(anchor_region.width, 50, 1200)
        self._anchor_height = self._create_spinbox(anchor_region.height, 50, 800)
        self._offset_x = self._create_spinbox(anchor_offset.x, -300, 600)
        self._offset_y = self._create_spinbox(anchor_offset.y, -300, 600)

        region_form.addRow("Anchor Left", self._anchor_left)
        region_form.addRow("Anchor Top", self._anchor_top)
        region_form.addRow("Anchor Width", self._anchor_width)
        region_form.addRow("Anchor Height", self._anchor_height)
        region_form.addRow("Offset X", self._offset_x)
        region_form.addRow("Offset Y", self._offset_y)
        layout.addLayout(region_form)

        self._anchor_left.valueChanged.connect(self._on_region_change)
        self._anchor_top.valueChanged.connect(self._on_region_change)
        self._anchor_width.valueChanged.connect(self._on_region_change)
        self._anchor_height.valueChanged.connect(self._on_region_change)
        self._offset_x.valueChanged.connect(self._on_offset_change)
        self._offset_y.valueChanged.connect(self._on_offset_change)

        buttons = QHBoxLayout()
        reload_button = QPushButton("Reload Templates", group)
        reload_button.clicked.connect(self._reload_anchor_templates)
        buttons.addWidget(reload_button)

        realign_button = QPushButton("Realign Now", group)
        realign_button.clicked.connect(self._manual_realign)
        buttons.addWidget(realign_button)

        open_button = QPushButton("Open Template Folder", group)
        open_button.clicked.connect(self._open_anchor_directory)
        buttons.addWidget(open_button)

        layout.addLayout(buttons)
        return group

    def _create_spinbox(self, value: int, minimum: int, maximum: int) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(value)
        return spinbox

    def _toggle_auto_align(self) -> None:
        publish_ui_action(
            UiActionType.TOGGLE_AUTO_ALIGNMENT,
            {"enabled": self._auto_align_checkbox.isChecked()},
        )

    def _toggle_anchor_overlay_visibility(self) -> None:
        publish_ui_action(
            UiActionType.TOGGLE_ANCHOR_OVERLAY,
            {"visible": self._anchor_overlay_checkbox.isChecked()},
        )

    def _update_alignment_interval(self, value: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_ALIGNMENT_POLL_INTERVAL,
            {"value": value},
        )

    def _update_threshold(self, value: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_ANCHOR_THRESHOLD,
            {"value": value / 100.0},
        )

    def _on_region_change(self, _: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_ANCHOR_REGION,
            {
                "left": self._anchor_left.value(),
                "top": self._anchor_top.value(),
                "width": self._anchor_width.value(),
                "height": self._anchor_height.value(),
            },
        )

    def _on_anchor_overlay_visibility_change(self, visible: bool) -> None:
        self._anchor_overlay_checkbox.setChecked(visible)

    def _on_offset_change(self, _: int) -> None:
        publish_ui_action(
            UiActionType.UPDATE_ANCHOR_OFFSET,
            {"x": self._offset_x.value(), "y": self._offset_y.value()},
        )

    def _run_auto_alignment(self) -> bool:
        publish_ui_action(UiActionType.MANUAL_REALIGN)
        return True

    def _reload_anchor_templates(self) -> None:
        publish_ui_action(UiActionType.RELOAD_ANCHOR_TEMPLATES)

    def _manual_realign(self) -> None:
        publish_ui_action(UiActionType.MANUAL_REALIGN)

    def _open_anchor_directory(self) -> None:
        publish_ui_action(UiActionType.OPEN_ANCHOR_DIRECTORY)
