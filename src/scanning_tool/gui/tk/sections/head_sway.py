"""Head Sway Compensation section — anchor tracking and auto-alignment."""
from __future__ import annotations


import os
import subprocess
import sys
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from scanning_tool.config import ensure_anchor_directory
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentRequest
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.capture_provider import ScreenCaptureProvider

from ..overlays import (
    hide_anchor_overlay,
    register_anchor_sliders,
    show_anchor_overlay,
    sync_anchor_sliders,
    update_anchor_overlay_region,
)
from ..widgets import (
    create_button_row,
    create_glass_scale,
    create_labeled_spinbox,
)


from typing import TYPE_CHECKING

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
        self._apply_anchor_change(
            self._update_anchor_region,
            lambda: f"Anchor region updated: {self._ctx.config.anchor_template}",
            update_overlay=True,
        )

    def _on_offset_change(self, *_args: object) -> None:
        self._apply_anchor_change(
            self._update_anchor_offset,
            lambda: f"Anchor offset updated: {self._ctx.config.anchor_offset}",
        )

    def _apply_anchor_change(
        self,
        update: Callable[[], None],
        status_message: Callable[[], str],
        update_overlay: bool = False,
    ) -> None:
        if self._ctx.control_state.syncing.anchor:
            return

        update()
        self._status.set_anchor(status_message(), hold=2.0)

        if self._ctx.config.auto_alignment.enabled:
            self._run_auto_alignment()

        if update_overlay:
            update_anchor_overlay_region(self._ctx.overlay_state)

    def _update_anchor_region(self) -> None:
        anchor_region = self._ctx.config.anchor_template
        anchor_region.left = int(self._anchor_left.get())
        anchor_region.top = int(self._anchor_top.get())
        anchor_region.width = int(self._anchor_width.get())
        anchor_region.height = int(self._anchor_height.get())

    def _update_anchor_offset(self) -> None:
        anchor_offset = self._ctx.config.anchor_offset
        anchor_offset.x = int(self._offset_x.get())
        anchor_offset.y = int(self._offset_y.get())

    def _toggle_auto_align(self) -> None:
        self._ctx.config.auto_alignment.enabled = self._auto_align_var.get()
        self._ctx.scan_state.last_alignment_info.enabled = (
            self._ctx.config.auto_alignment.enabled
        )
        self._ctx.scan_state.notify_alignment_info_listeners()
        if self._ctx.config.auto_alignment.enabled:
            self._status.set_anchor("Head sway compensation enabled.")
            self._run_auto_alignment()
        else:
            self._status.set_anchor("Head sway compensation disabled.")

    def _run_auto_alignment(self) -> bool:

        result = alignment_service.align(
            self._ctx.scan_state.anchor_tracker,
            self._ctx.scan_state.last_alignment_info,
            AlignmentRequest.from_config(self._ctx.config),
        )
        self._ctx.scan_state.notify_alignment_info_listeners()
        return result

    def _toggle_anchor_overlay_visibility(self) -> None:
        self._ctx.overlay_state.anchor_overlay_visible = self._anchor_overlay_var.get()
        if self._ctx.overlay_state.anchor_overlay_visible:
            show_anchor_overlay(
                self._ctx.overlay_state, self._ctx.config.anchor_template,
            )
            self._status.set_anchor("Anchor overlay shown.")
        else:
            hide_anchor_overlay(self._ctx.overlay_state)
            self._status.set_anchor("Anchor overlay hidden.")

    def _update_alignment_interval(self, *_args: object) -> None:
        try:
            value = int(self._interval_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(100, min(5000, value))
        self._ctx.config.alignment_poll_interval_ms = value
        self._status.set_anchor(
            f"Alignment interval set to {self._ctx.config.alignment_poll_interval_ms} ms",
            hold=2.0,
        )

    def _update_threshold(self, *_args: object) -> None:
        try:
            value = float(self._threshold_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(0.1, min(0.99, value))
        self._ctx.config.anchor_threshold = value
        if self._ctx.scan_state.anchor_tracker is not None:
            self._ctx.scan_state.anchor_tracker.set_threshold(
                self._ctx.config.anchor_threshold,
            )
        self._status.set_anchor(
            f"Anchor detection threshold set to {self._ctx.config.anchor_threshold:.2f}",
        )

    def _reload_anchor_templates(self) -> None:
        ensure_anchor_directory(self._ctx.config.anchor_template_dir)
        if self._ctx.scan_state.anchor_tracker is None:
            self._ctx.scan_state.anchor_tracker = AnchorRegionTracker(
                self._ctx.config.anchor_template_dir,
                ScreenCaptureProvider(),
                self._ctx.config.anchor_threshold,
            )
        count = self._ctx.scan_state.anchor_tracker.set_directory(
            self._ctx.config.anchor_template_dir,
        )
        self._status.set_anchor(
            f"Loaded {count} anchor template(s) from {self._ctx.config.anchor_template_dir}.",
        )

    def _manual_realign(self) -> None:
        if self._run_auto_alignment():
            info = self._ctx.scan_state.last_alignment_info
            self._status.set_anchor(
                f"Anchor locked using {info.template} (score {info.score:.2f}).",
                hold=2.5,
            )
            self._status.set_status(
                f"Auto alignment adjusted CAP_REGION: {self._ctx.config.capture_region}",
            )
        else:
            self._status.set_anchor(
                "Anchor match not found. Adjust search region or add templates.",
            )

    def _open_anchor_directory(self) -> None:
        path = os.path.abspath(self._ctx.config.anchor_template_dir)
        ensure_anchor_directory(path)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as exc:
            self._status.set_anchor(f"Unable to open template folder: {exc}", hold=3.0)
        else:
            self._status.set_anchor(f"Opened template folder: {path}")
