"""Controls section — continuous capture interval + primary action buttons."""

import tkinter as tk
from tkinter import ttk

from .base import SectionContext
from ..widgets import create_labeled_spinbox, create_section_row
from ..overlays import (
    choose_label_color,
    hide_capture_overlay,
    show_capture_overlay,
    toggle_border,
    update_overlay_region,
)


class ControlsSection:
    """Capture-interval spinbox and the six primary action buttons."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Controls", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status

        self._interval_var = tk.DoubleVar(
            value=float(ctx.config.continuous_capture_interval)
        )
        create_labeled_spinbox(
            frame,
            text="Continuous capture interval (s)",
            variable=self._interval_var,
            from_=0.2,
            to=30.0,
            increment=0.1,
            width=6,
            command=self._on_interval_change,
            colors=ctx.colors,
        )
        self._interval_var.trace_add("write", self._on_interval_change)

        button_row = create_section_row(frame)
        ttk.Button(
            button_row,
            text="Single Scan",
            command=ctx.capture_service.capture_once,
            style="Glass.TButton",
        ).pack(side="left", padx=5)
        self._continuous_button_text = tk.StringVar(
            value=self._build_continuous_button_label()
        )
        ttk.Button(
            button_row,
            textvariable=self._continuous_button_text,
            command=self._toggle_continuous_capture,
            style="Glass.TButton",
        ).pack(side="left", padx=5)
        self._capture_box_button_text = tk.StringVar(
            value=self._build_capture_box_button_label()
        )
        ttk.Button(
            button_row,
            textvariable=self._capture_box_button_text,
            command=self._toggle_capture_box,
            style="Glass.TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            button_row,
            text="Update Overlay",
            command=update_overlay_region,
            style="Glass.TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            button_row,
            text="Set Label Color",
            command=choose_label_color,
            style="Glass.TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            button_row,
            text="Save Config",
            command=ctx.config_service.save,
            style="Glass.TButton",
        ).pack(side="left", padx=5)

        return frame

    def _on_interval_change(self, *_args: object) -> None:
        try:
            value = float(self._interval_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(0.2, min(30.0, value))
        self._ctx.config.continuous_capture_interval = value
        self._status.set_status(
            f"Continuous capture interval set to {self._ctx.config.continuous_capture_interval:.1f}s"
        )

    def _build_continuous_button_label(self) -> str:
        return (
            "Stop Auto Scan"
            if self._ctx.scan_state.continuous_mode
            else "Start Auto Scan"
        )

    def _build_capture_box_button_label(self) -> str:
        return (
            "Hide Capture Box"
            if self._is_capture_box_visible()
            else "Show Capture Box"
        )

    def _is_capture_box_visible(self) -> bool:
        return bool(self._ctx.overlay_state.capture_overlay_root)

    def _toggle_capture_box(self) -> None:
        if self._is_capture_box_visible():
            hide_capture_overlay(self._ctx.overlay_state)
            self._capture_box_button_text.set("Show Capture Box")
            self._status.set_status("Capture box hidden.")
        else:
            show_capture_overlay(
                self._ctx.overlay_state,
                self._ctx.config.capture_region,
            )
            self._capture_box_button_text.set("Hide Capture Box")
            self._status.set_status("Capture box shown.")

    def _toggle_continuous_capture(self) -> None:
        self._ctx.capture_service.toggle_continuous()
        self._continuous_button_text.set(self._build_continuous_button_label())
        self._status.set_status(
            "Auto scan started." if self._ctx.scan_state.continuous_mode else "Auto scan stopped."
        )
