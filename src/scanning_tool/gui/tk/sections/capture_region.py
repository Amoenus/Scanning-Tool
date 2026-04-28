"""Capture Region section — 4 sliders controlling the OCR capture rectangle via AppContext capture settings."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action

from ..overlays import (
    register_capture_sliders,
    sync_capture_sliders,
)
from ..widgets import create_glass_scale

if TYPE_CHECKING:
    from .base import SectionContext
class CaptureRegionSection:
    """Left/Top/Width/Height sliders bound to ``app_state.cap_region``."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Capture Region", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._status = ctx.status
        self._ctx = ctx

        cap_region = ctx.config.capture_region

        self._left = self._make_capture_scale(frame, "Left", 0, 3000, cap_region.left)
        self._top = self._make_capture_scale(frame, "Top", 0, 2000, cap_region.top)
        self._width = self._make_capture_scale(
            frame, "Width", 50, 1000, cap_region.width,
        )
        self._height = self._make_capture_scale(
            frame, "Height", 20, 500, cap_region.height, padding=(0, 0),
        )

        register_capture_sliders(
            self._left,
            self._top,
            self._width,
            self._height,
            self._ctx.control_state,
        )
        sync_capture_sliders(self._ctx.control_state, cap_region)
        self._build_border_visibility_checkbox(frame)
        return frame

    def _build_border_visibility_checkbox(self, parent: ttk.Widget) -> None:
        self._border_var = tk.BooleanVar(value=self._ctx.overlay_state.show_border)
        ttk.Checkbutton(
            parent,
            text="Show capture border",
            variable=self._border_var,
            command=self._toggle_capture_border,
            style="Glass.TCheckbutton",
        ).pack(anchor="w", padx=5, pady=(0, 5))

    def _toggle_capture_border(self) -> None:
        publish_ui_action(UiActionType.TOGGLE_CAPTURE_BORDER)
        self._border_var.set(self._ctx.overlay_state.show_border)

    def _make_capture_scale(
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
        if self._ctx.control_state.syncing.capture:
            return
        publish_ui_action(
            UiActionType.UPDATE_CAPTURE_REGION,
            {
                "left": int(self._left.get()),
                "top": int(self._top.get()),
                "width": int(self._width.get()),
                "height": int(self._height.get()),
            },
        )
