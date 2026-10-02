"""Controls section — continuous capture interval + primary action buttons."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.scan import ScanAction

from ..overlays.base import safe_tk
from ..widgets import (
    create_button_row,
    create_labeled_spinbox,
)

if TYPE_CHECKING:
    from .base import SectionContext


class ControlsSection:
    """Capture-interval spinbox and the six primary action buttons."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Controls", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status

        self._interval_var = tk.DoubleVar(
            value=float(ctx.config.continuous_capture_interval),
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
            value=self._build_continuous_button_label(),
        )
        self._capture_box_button_text = tk.StringVar(
            value=self._build_capture_box_button_label(),
        )

        create_button_row(
            frame,
            [
                ("Single Scan", self._start_single_scan),
                (self._continuous_button_text, self._toggle_continuous_capture),
                (self._capture_box_button_text, self._toggle_capture_box),
                ("Update Overlay", self._update_overlay_region),
                ("Set Label Color", self._choose_label_color),
                ("Save Config", self._save_config),
            ],
        )

        self._ctx.scan_state.add_continuous_mode_listener(
            self._on_continuous_mode_change,
        )
        self._ctx.overlay_state.add_capture_overlay_root_listener(
            self._on_capture_overlay_visibility_change,
        )
        return frame

    def _on_interval_change(self, *_args: object) -> None:
        try:
            value = float(self._interval_var.get())
        except (tk.TclError, ValueError):
            return
        value = max(0.2, min(30.0, value))
        publish_ui_action(
            ConfigAction.UPDATE_CONTINUOUS_CAPTURE_INTERVAL,
            {"value": value},
        )

    def _start_single_scan(self) -> None:
        publish_ui_action(ScanAction.SINGLE_SCAN)

    def _on_continuous_mode_change(self, continuous_mode: bool) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._continuous_button_text.set(
                    self._build_continuous_button_label(),
                ),
            ),
        )

    def _build_continuous_button_label(self) -> str:
        return "Stop Auto Scan" if self._ctx.scan_state.continuous_mode else "Start Auto Scan"

    def _build_capture_box_button_label(self) -> str:
        return "Hide Capture Box" if self._is_capture_box_visible() else "Show Capture Box"

    def _is_capture_box_visible(self) -> bool:
        return bool(self._ctx.overlay_state.capture_overlay_root)

    def _toggle_capture_box(self) -> None:
        publish_ui_action(
            ConfigAction.TOGGLE_CAPTURE_BOX,
            {"visible": not self._is_capture_box_visible()},
        )

    def _on_capture_overlay_visibility_change(
        self,
        capture_root: Any | None,
    ) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._capture_box_button_text.set(
                    self._build_capture_box_button_label(),
                ),
            ),
        )

    def _toggle_continuous_capture(self) -> None:
        publish_ui_action(ScanAction.TOGGLE_CONTINUOUS_CAPTURE)

    def _update_overlay_region(self) -> None:
        publish_ui_action(ConfigAction.UPDATE_OVERLAY_REGION)

    def _choose_label_color(self) -> None:
        publish_ui_action(ConfigAction.CHOOSE_LABEL_COLOR)

    def _save_config(self) -> None:
        publish_ui_action(ConfigAction.SAVE_CONFIG)
