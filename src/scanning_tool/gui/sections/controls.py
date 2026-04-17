"""Controls section — continuous capture interval + primary action buttons."""

import tkinter as tk
from tkinter import ttk

from scanning_tool.gui.sections.base import SectionContext
from scanning_tool.gui.widgets import create_button_row, create_labeled_spinbox
from scanning_tool.gui.overlays import (
    choose_label_color,
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

        create_button_row(
            frame,
            [
                ("Single Scan", ctx.capture_service.capture_once),
                ("Loop Toggle", ctx.capture_service.toggle_continuous),
                ("Update Overlay", update_overlay_region),
                ("Set Label Color", choose_label_color),
                ("Save Config", ctx.save_config),
                ("Toggle Border", toggle_border),
            ],
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
