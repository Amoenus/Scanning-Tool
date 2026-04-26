"""Controls section — continuous capture interval + primary action buttons."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional

from .base import SectionContext
from ..overlays import (
    choose_label_color,
    hide_capture_overlay,
    show_capture_overlay,
    update_overlay_region,
)
from ..overlays.base import safe_tk
from ..widgets import (
    create_button_row,
    create_labeled_spinbox,
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

        self._continuous_button_text = tk.StringVar(
            value=self._build_continuous_button_label()
        )
        self._capture_box_button_text = tk.StringVar(
            value=self._build_capture_box_button_label()
        )

        create_button_row(
            frame,
            [
                ("Single Scan", ctx.capture_service.capture_once),
                (self._continuous_button_text, self._toggle_continuous_capture),
                (self._capture_box_button_text, self._toggle_capture_box),
                ("Update Overlay", update_overlay_region),
                ("Set Label Color", choose_label_color),
                ("Save Config", ctx.config_service.save),
            ],
        )

        self._ctx.scan_state.add_continuous_mode_listener(
            self._on_continuous_mode_change
        )
        self._ctx.overlay_state.add_capture_overlay_root_listener(
            self._on_capture_overlay_visibility_change
        )
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

    def _on_continuous_mode_change(self, continuous_mode: bool) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._continuous_button_text.set(
                    self._build_continuous_button_label()
                ),
            )
        )

    def _build_continuous_button_label(self) -> str:
        return (
            "Stop Auto Scan"
            if self._ctx.scan_state.continuous_mode
            else "Start Auto Scan"
        )

    def _build_capture_box_button_label(self) -> str:
        return (
            "Hide Capture Box" if self._is_capture_box_visible() else "Show Capture Box"
        )

    def _is_capture_box_visible(self) -> bool:
        return bool(self._ctx.overlay_state.capture_overlay_root)

    def _toggle_capture_box(self) -> None:
        if self._is_capture_box_visible():
            hide_capture_overlay(self._ctx.overlay_state)
            self._status.set_status("Capture box hidden.")
        else:
            show_capture_overlay(
                self._ctx.overlay_state,
                self._ctx.config.capture_region,
            )
            self._status.set_status("Capture box shown.")

    def _on_capture_overlay_visibility_change(
        self,
        capture_root: Optional[Any],
    ) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._capture_box_button_text.set(
                    self._build_capture_box_button_label()
                ),
            )
        )

    def _toggle_continuous_capture(self) -> None:
        self._ctx.capture_service.toggle_continuous()
        self._on_continuous_mode_change(self._ctx.scan_state.continuous_mode)
        self._status.set_status(
            "Auto scan started."
            if self._ctx.scan_state.continuous_mode
            else "Auto scan stopped."
        )
