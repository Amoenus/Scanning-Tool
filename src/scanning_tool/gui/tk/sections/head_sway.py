"""Head Sway Compensation section — anchor tracking and auto-alignment."""
from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import TYPE_CHECKING

from scanning_tool.state.actions import ConfigAction
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.state.actions.runtime import RuntimeAction

from ..overlays import (
    register_anchor_sliders,
    sync_anchor_sliders,
)
from ..overlays.base import safe_tk
from ..widgets import (
    create_button_row,
    create_glass_scale,
    create_labeled_spinbox,
)

if TYPE_CHECKING:
    from .base import SectionContext
class HeadSwaySection:
    """Anchor region + offset sliders, threshold, and alignment controls."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent, text="Head Sway Compensation", style="Glass.TLabelframe",
        )
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status

        self._auto_align_var = tk.BooleanVar(value=ctx.config.auto_alignment.enabled)
        ttk.Checkbutton(
            frame,
            text="Enable auto alignment",
            variable=self._auto_align_var,
            command=self._toggle_auto_align,
            style="Glass.TCheckbutton",
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self._anchor_overlay_var = tk.BooleanVar(
            value=ctx.overlay_state.anchor_overlay_visible,
        )
        ttk.Checkbutton(
            frame,
            text="Show anchor overlay",
            variable=self._anchor_overlay_var,
            command=self._toggle_anchor_overlay_visibility,
            style="Glass.TCheckbutton",
        ).pack(anchor="w", padx=5, pady=(0, 5))
        ctx.overlay_state.add_anchor_overlay_visibility_listener(
            self._on_anchor_overlay_visibility_change,
        )

        self._build_interval_row(frame, ctx)
        self._build_threshold_row(frame, ctx)
        self._build_region_sliders(frame)
        self._build_action_buttons(frame)

        return frame

    def _build_interval_row(self, parent: ttk.Widget, ctx: SectionContext) -> None:
        self._interval_var = tk.IntVar(
            value=int(self._ctx.config.alignment_poll_interval_ms),
        )
        create_labeled_spinbox(
            parent,
            text="Alignment interval (ms)",
            variable=self._interval_var,
            from_=100,
            to=5000,
            increment=50,
            width=6,
            command=self._update_alignment_interval,
            colors=ctx.colors,
        )
        self._interval_var.trace_add("write", self._update_alignment_interval)

    def _build_threshold_row(self, parent: ttk.Widget, ctx: SectionContext) -> None:
        self._threshold_var = tk.DoubleVar(value=self._ctx.config.anchor_threshold)
        create_labeled_spinbox(
            parent,
            text="Detection threshold",
            variable=self._threshold_var,
            from_=0.10,
            to=0.99,
            increment=0.01,
            width=6,
            command=self._update_threshold,
            colors=ctx.colors,
        )
        self._threshold_var.trace_add("write", self._update_threshold)

    def _make_scale(
        self,
        parent: ttk.Widget,
        text: str,
        minimum: float,
        maximum: float,
        initial: float,
        command: Callable[[str], None],
        padding: tuple[int, int] = (0, 4),
    ) -> ttk.Scale:
        return create_glass_scale(
            parent,
            text=text,
            minimum=minimum,
            maximum=maximum,
            initial=initial,
            command=command,
            padding=padding,
        )

    def _create_anchor_slider(
        self,
        parent: ttk.Widget,
        text: str,
        minimum: float,
        maximum: float,
        initial: float,
        command: Callable[[str], None],
        padding: tuple[int, int] = (0, 4),
    ) -> ttk.Scale:
        return self._make_scale(
            parent,
            text=text,
            minimum=minimum,
            maximum=maximum,
            initial=initial,
            command=command,
            padding=padding,
        )

    def _build_region_sliders(self, parent: ttk.Widget) -> None:
        anchor_region = self._ctx.config.anchor_template
        anchor_offset = self._ctx.config.anchor_offset

        slider_configs = [
            (
                "Anchor Left",
                0,
                3840,
                anchor_region.left,
                self._on_region_change,
                (0, 4),
            ),
            ("Anchor Top", 0, 2160, anchor_region.top, self._on_region_change, (0, 4)),
            (
                "Anchor Width",
                50,
                1200,
                anchor_region.width,
                self._on_region_change,
                (0, 4),
            ),
            (
                "Anchor Height",
                50,
                800,
                anchor_region.height,
                self._on_region_change,
                (0, 4),
            ),
            ("Offset X", -300, 600, anchor_offset.x, self._on_offset_change, (0, 4)),
            ("Offset Y", -300, 600, anchor_offset.y, self._on_offset_change, (0, 0)),
        ]

        (
            self._anchor_left,
            self._anchor_top,
            self._anchor_width,
            self._anchor_height,
            self._offset_x,
            self._offset_y,
        ) = [self._create_anchor_slider(parent, *config) for config in slider_configs]

        register_anchor_sliders(
            self._anchor_left,
            self._anchor_top,
            self._anchor_width,
            self._anchor_height,
            self._offset_x,
            self._offset_y,
            self._ctx.control_state,
        )
        sync_anchor_sliders(
            self._ctx.control_state,
            self._ctx.config.anchor_template,
            self._ctx.config.anchor_offset,
        )

    def _build_action_buttons(self, parent: ttk.Widget) -> None:
        create_button_row(
            parent,
            [
                ("Reload Templates", self._reload_anchor_templates),
                ("Realign Now", self._manual_realign),
                ("Open Template Folder", self._open_anchor_directory),
            ],
        )

    def _on_region_change(self, *_args: object) -> None:
        if self._ctx.control_state.syncing.anchor:
            return

        publish_ui_action(
            ConfigAction.UPDATE_ANCHOR_REGION,
            {
                "left": int(self._anchor_left.get()),
                "top": int(self._anchor_top.get()),
                "width": int(self._anchor_width.get()),
                "height": int(self._anchor_height.get()),
            },
        )

    def _on_offset_change(self, *_args: object) -> None:
        if self._ctx.control_state.syncing.anchor:
            return

        publish_ui_action(
            ConfigAction.UPDATE_ANCHOR_OFFSET,
            {
                "x": int(self._offset_x.get()),
                "y": int(self._offset_y.get()),
            },
        )

    def _toggle_auto_align(self) -> None:
        publish_ui_action(
            ConfigAction.TOGGLE_AUTO_ALIGNMENT,
            {"enabled": self._auto_align_var.get()},
        )

    def _toggle_anchor_overlay_visibility(self) -> None:
        publish_ui_action(
            ConfigAction.TOGGLE_ANCHOR_OVERLAY,
            {"visible": self._anchor_overlay_var.get()},
        )

    def _on_anchor_overlay_visibility_change(self, visible: bool) -> None:
        safe_tk(lambda: self._anchor_overlay_var.set(visible))

    def _update_alignment_interval(self, *_args: object) -> None:
        try:
            value = int(self._interval_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(100, min(5000, value))
        publish_ui_action(
            ConfigAction.UPDATE_ALIGNMENT_POLL_INTERVAL,
            {"value": value},
        )

    def _update_threshold(self, *_args: object) -> None:
        try:
            value = float(self._threshold_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(0.1, min(0.99, value))
        publish_ui_action(
            ConfigAction.UPDATE_ANCHOR_THRESHOLD,
            {"value": value},
        )

    def _reload_anchor_templates(self) -> None:
        publish_ui_action(ConfigAction.RELOAD_ANCHOR_TEMPLATES)

    def _manual_realign(self) -> None:
        publish_ui_action(RuntimeAction.MANUAL_REALIGN)

    def _open_anchor_directory(self) -> None:
        publish_ui_action(ConfigAction.OPEN_ANCHOR_DIRECTORY)
