"""Result Display section — offset sliders for the on-screen info overlay via AppContext overlay settings."""
from __future__ import annotations

from tkinter import ttk
from typing import TYPE_CHECKING

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.state.actions import ConfigAction

from ..overlays import (
    register_overlay_sliders,
    sync_overlay_sliders,
)
from ..widgets import create_glass_scale

if TYPE_CHECKING:
    from .base import SectionContext
class ResultDisplaySection:
    """Display offset X/Y sliders bound to ``app_state.info_overlay_offset``."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Result Display", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status

        overlay_offset = ctx.config.overlay_config.info_offset

        self._offset_x = self._make_offset_scale(
            frame, "Display offset X", -800, 800, overlay_offset.x,
        )
        self._offset_y = self._make_offset_scale(
            frame, "Display offset Y", -600, 600, overlay_offset.y, padding=(0, 0),
        )

        register_overlay_sliders(
            self._offset_x,
            self._offset_y,
            self._ctx.control_state,
        )
        sync_overlay_sliders(
            self._ctx.control_state,
            self._ctx.config.overlay_config.info_offset,
        )
        return frame

    def _make_offset_scale(
        self,
        parent: ttk.Widget,
        text: str,
        minimum: float,
        maximum: float,
        initial: float,
        padding: tuple[int, int] = (0, 4),
    ) -> ttk.Scale:
        return create_glass_scale(parent, text=text, minimum=minimum, maximum=maximum, initial=initial, command=self._on_change, padding=padding)

    def _on_change(self, *_args: object) -> None:
        if self._ctx.control_state.syncing.overlay:
            return
        publish_ui_action(
            ConfigAction.UPDATE_RESULT_DISPLAY_OFFSET,
            {
                "x": int(self._offset_x.get()),
                "y": int(self._offset_y.get()),
            },
        )
