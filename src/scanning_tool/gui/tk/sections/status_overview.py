"""Runtime status section for build-time and current scanner state."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from scanning_tool.ollama import get_ollama_host, get_ollama_model, is_model_running
from scanning_tool.state.signals import ollama_status_updated

from ..overlays.base import safe_tk
from ..widgets import create_section_row, create_status_label

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AlignmentInfo
    from scanning_tool.domain.capture import ScanResult

    from .base import SectionContext
class StatusOverviewSection:
    """Status panel that keeps key runtime state visible in the GUI."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Runtime Status", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._host_var = tk.StringVar()
        self._capture_var = tk.StringVar()
        self._auto_scan_var = tk.StringVar()
        self._auto_align_var = tk.StringVar()
        self._last_scan_var = tk.StringVar()

        self._host_badge = self._create_badge(frame, "Ollama host", self._host_var)
        self._ollama_status_var = tk.StringVar()
        self._ollama_status_badge = self._create_badge(frame, "Ollama status", self._ollama_status_var)
        self._capture_badge = self._create_badge(
            frame, "Capture box", self._capture_var,
        )
        self._auto_scan_badge = self._create_badge(
            frame, "Auto scan", self._auto_scan_var,
        )
        self._auto_align_badge = self._create_badge(
            frame, "Auto align", self._auto_align_var,
        )
        create_status_label(frame, self._last_scan_var)
        create_status_label(frame, self._ctx.status.status_var)
        create_status_label(frame, self._ctx.status.anchor_status_var)

        hotkey_row = create_section_row(frame, pady=(0, 2))
        ttk.Label(
            hotkey_row,
            text="Hotkeys: 7 = Single Scan · Ctrl+7 = Toggle Auto Scan · 8 = Show/Hide Capture Box",
            style="Glass.Small.TLabel",
            wraplength=660,
            justify="left",
        ).pack(fill="x", padx=5)

        self._refresh_status()
        self._ctx.scan_state.add_continuous_mode_listener(
            self._on_continuous_mode_change,
        )
        self._ctx.scan_state.add_scan_result_listener(self._on_scan_result_change)
        self._ctx.scan_state.add_alignment_info_listener(self._on_alignment_info_change)
        self._ctx.overlay_state.add_capture_overlay_root_listener(
            self._on_capture_overlay_visibility_change,
        )
        ollama_status_updated.connect(self._on_ollama_status_updated, weak=False)
        from scanning_tool.state.signals import ollama_readiness_changed

        ollama_readiness_changed.connect(
            self._on_ollama_readiness_changed,
            weak=False,
        )
        self._schedule_host_model_refresh()
        return frame

    def _create_badge(
        self,
        parent: ttk.Widget,
        label_text: str,
        variable: tk.StringVar,
    ) -> tk.Label:
        row = create_section_row(parent, pady=(0, 2))
        ttk.Label(row, text=f"{label_text}: ", style="Glass.Small.TLabel").pack(
            side="left",
        )
        badge = tk.Label(
            row,
            textvariable=variable,
            bg="#294452",
            fg="#ffffff",
            relief="ridge",
            borderwidth=1,
            padx=8,
            pady=4,
            anchor="w",
            justify="left",
            font=("Segoe UI", 9, "bold"),
        )
        badge.pack(side="left", fill="x", expand=True)
        return badge

    def _schedule_host_model_refresh(self) -> None:
        self._ctx.root.after(1000, self._periodic_host_model_refresh)

    def _periodic_host_model_refresh(self) -> None:
        self._refresh_host_model_status()
        self._refresh_ollama_status_badge(None)
        self._schedule_host_model_refresh()

    def _refresh_status(self) -> None:
        self._refresh_host_model_status()
        self._refresh_ollama_status_badge(None)
        self._refresh_capture_badge()
        self._refresh_auto_scan_badge(self._ctx.scan_state.continuous_mode)
        self._refresh_auto_align_badge(self._ctx.scan_state.last_alignment_info)
        self._refresh_last_scan_badge(self._ctx.scan_state.last_result)

    def _refresh_host_model_status(self) -> None:
        self._host_var.set(get_ollama_host())

    def _on_continuous_mode_change(self, continuous_mode: bool) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._refresh_auto_scan_badge(continuous_mode),
            ),
        )

    def _on_scan_result_change(self, scan_result: ScanResult | None) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._refresh_last_scan_badge(scan_result),
            ),
        )

    def _on_alignment_info_change(self, alignment_info: AlignmentInfo) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._refresh_auto_align_badge(alignment_info),
            ),
        )

    def _on_capture_overlay_visibility_change(
        self,
        capture_root: Any | None,
    ) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                self._refresh_capture_badge,
            ),
        )

    def _refresh_capture_badge(self) -> None:
        text = "Visible" if self._is_capture_visible() else "Hidden"
        self._capture_var.set(text)
        self._update_badge_color(self._capture_badge, text)

    def _refresh_auto_scan_badge(self, continuous_mode: bool) -> None:
        text = "Active" if continuous_mode else "Inactive"
        self._auto_scan_var.set(text)
        self._update_badge_color(self._auto_scan_badge, text)

    def _refresh_auto_align_badge(self, alignment_info: AlignmentInfo) -> None:
        self._auto_align_var.set(self._build_auto_align_text(alignment_info))
        self._update_badge_color(self._auto_align_badge, self._auto_align_var.get())

    def _refresh_ollama_status_badge(self, status_text: str | None) -> None:
        if status_text is None:
            status_text = self._build_default_ollama_status()
        self._ollama_status_var.set(status_text)
        self._update_badge_color(self._ollama_status_badge, status_text)

    def _build_default_ollama_status(self) -> str:
        model = get_ollama_model()
        if model and is_model_running(model):
            return f"Model {model} is currently running."
        return "Waiting for Ollama status."

    def _on_ollama_readiness_changed(
        self,
        sender: object,
        **kwargs: object,
    ) -> None:
        def update() -> None:
            self._refresh_host_model_status()
            ready = kwargs.get("ready")
            model = kwargs.get("model") or get_ollama_model()
            if ready is True and model:
                status = f"Model {model} is currently running."
            elif ready is False and model:
                status = f"Model {model} is not ready."
            else:
                status = self._build_default_ollama_status()
            self._refresh_ollama_status_badge(status)

        safe_tk(lambda: self._ctx.root.after(0, update))

    def _refresh_last_scan_badge(self, result: ScanResult | None) -> None:
        if result is None:
            self._last_scan_var.set("Last scan: none")
            return

        if result.info is None:
            if result.code_raw:
                self._last_scan_var.set(
                    f"Last scan: no deposit metadata for {result.code_raw}",
                )
                return
            self._last_scan_var.set("Last scan: no code extracted")
            return

        name = result.info.name or result.label or "Unknown"
        self._last_scan_var.set(f"Last scan: {name} ({result.label})")

    def _on_ollama_status_updated(self, sender: object, **kwargs: object) -> None:
        safe_tk(
            lambda: self._ctx.root.after(
                0,
                lambda: self._refresh_ollama_status_badge(
                    str(kwargs.get("message", "Ollama status updated.")),
                ),
            ),
        )

    def _is_capture_visible(self) -> bool:
        return bool(self._ctx.overlay_state.capture_overlay_root)

    def _build_auto_align_text(self, info: AlignmentInfo) -> str:
        if not info.enabled:
            return "Disabled"
        if info.matched:
            template = info.template or "template"
            score = f"{info.score:.2f}"
            return f"Matched ({template} / {score})"
        return "Active (searching)"

    def _build_last_scan_text(self) -> str:
        result = self._ctx.scan_state.last_result
        if result is None:
            return "Last scan: none"

        if result.info is None:
            if result.code_raw:
                return f"Last scan: no deposit metadata for {result.code_raw}"
            return "Last scan: no code extracted"

        name = result.info.name or result.label or "Unknown"
        return f"Last scan: {name} ({result.label})"

    def _update_badge_color(self, badge: tk.Label, value: str) -> None:
        if "Visible" in value or "Active" in value or "running" in value:
            color = "#2f8f4a"
        elif "Hidden" in value or "Inactive" in value:
            color = "#9a2f2f"
        else:
            color = "#2f85b5"
        badge.config(bg=color)
