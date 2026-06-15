"""Runtime status section for the Qt scanning tool GUI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from scanning_tool.gui.qt.sections.base import SectionContext
from scanning_tool.ollama import get_ollama_host, get_ollama_model, is_model_running
from scanning_tool.state.signals import ollama_readiness_changed, ollama_status_updated, status_updated

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AlignmentInfo
    from scanning_tool.domain.capture import ScanResult


class StatusOverviewSection:
    """Status panel that shows runtime scanner state."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx

        group = QGroupBox("Runtime Status", parent)
        layout = QVBoxLayout(group)
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)

        self._host_label = self._make_badge(grid, 0, "Ollama host", get_ollama_host())
        self._ollama_status_label = self._make_badge(grid, 1, "Ollama status", self._default_ollama_status())
        self._capture_label = self._make_badge(grid, 2, "Capture box", self._capture_text())
        self._auto_scan_label = self._make_badge(grid, 3, "Auto scan", self._auto_scan_text())
        self._auto_align_label = self._make_badge(
            grid, 4, "Auto align", self._auto_align_text(ctx.scan_state.last_alignment_info),
        )

        layout.addLayout(grid)

        self._last_scan_label = QLabel(self._build_last_scan_text(ctx.scan_state.last_result), group)
        self._last_scan_label.setWordWrap(True)
        layout.addWidget(self._last_scan_label)

        self._status_label = QLabel(ctx.status.status_text, group)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        self._anchor_status_label = QLabel(ctx.status.anchor_status_text, group)
        self._anchor_status_label.setWordWrap(True)
        layout.addWidget(self._anchor_status_label)

        self._help_label = QLabel(
            "Hotkeys: 7 = Single Scan · Ctrl+7 = Toggle Auto Scan · 8 = Show/Hide Capture Box",
            group,
        )
        self._help_label.setWordWrap(True)
        layout.addWidget(self._help_label)

        ctx.scan_state.add_continuous_mode_listener(self._on_continuous_mode_change)
        ctx.scan_state.add_scan_result_listener(self._on_scan_result_change)
        ctx.scan_state.add_alignment_info_listener(self._on_alignment_info_change)
        ctx.overlay_state.add_capture_overlay_root_listener(self._on_capture_overlay_visibility_change)
        status_updated.connect(self._on_status_updated, weak=False)
        ollama_status_updated.connect(self._on_ollama_status_updated, weak=False)
        ollama_readiness_changed.connect(self._on_ollama_readiness_changed, weak=False)

        self._schedule_host_model_refresh()
        self._ctx = ctx
        return group

    def _make_badge(self, layout: QGridLayout, row: int, label: str, value: str) -> QLabel:
        label_widget = QLabel(f"{label}:", None)
        label_widget.setStyleSheet("font-weight: bold;")
        value_widget = QLabel(value, None)
        value_widget.setStyleSheet(self._badge_style(value))
        value_widget.setWordWrap(True)
        layout.addWidget(label_widget, row, 0)
        layout.addWidget(value_widget, row, 1)
        return value_widget

    def _schedule_host_model_refresh(self) -> None:
        QTimer.singleShot(1000, self._periodic_host_model_refresh)

    def _periodic_host_model_refresh(self) -> None:
        self._refresh_status()
        self._schedule_host_model_refresh()

    def _refresh_status(self) -> None:
        self._host_label.setText(get_ollama_host())
        self._ollama_status_label.setText(self._default_ollama_status())
        self._capture_label.setText(self._capture_text())
        self._capture_label.setStyleSheet(self._badge_style(self._capture_label.text()))
        self._auto_scan_label.setText(self._auto_scan_text())
        self._auto_scan_label.setStyleSheet(self._badge_style(self._auto_scan_label.text()))
        self._auto_align_label.setText(self._auto_align_text(self._ctx.scan_state.last_alignment_info))
        self._auto_align_label.setStyleSheet(self._badge_style(self._auto_align_label.text()))
        self._last_scan_label.setText(self._build_last_scan_text(self._ctx.scan_state.last_result))
        self._status_label.setText(self._ctx.status.status_text)
        self._anchor_status_label.setText(self._ctx.status.anchor_status_text)

    def _on_continuous_mode_change(self, continuous_mode: bool) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_scan_result_change(self, scan_result: ScanResult | None) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_alignment_info_change(self, alignment_info: AlignmentInfo) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_capture_overlay_visibility_change(self, capture_root: object | None) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_ollama_status_updated(self, sender: object, **kwargs: object) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_ollama_readiness_changed(self, sender: object, **kwargs: object) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _on_status_updated(self, sender: object, message: str) -> None:
        QTimer.singleShot(0, self._refresh_status)

    def _default_ollama_status(self) -> str:
        model = get_ollama_model()
        if model and is_model_running(model):
            return f"Model {model} is currently running."
        return "Waiting for Ollama status."

    def _capture_text(self) -> str:
        return "Visible" if bool(self._ctx.overlay_state.capture_overlay_root) else "Hidden"

    def _auto_scan_text(self) -> str:
        return "Active" if self._ctx.scan_state.continuous_mode else "Inactive"

    def _auto_align_text(self, alignment_info: AlignmentInfo | None) -> str:
        if alignment_info is None:
            return "Disabled"
        if not alignment_info.enabled:
            return "Disabled"
        if alignment_info.matched:
            template = alignment_info.template or "template"
            score = f"{alignment_info.score:.2f}"
            return f"Matched ({template} / {score})"
        return "Active (searching)"

    def _build_last_scan_text(self, result: ScanResult | None) -> str:
        if result is None:
            return "Last scan: none"
        if result.info is None:
            if result.code_raw:
                return f"Last scan: no deposit metadata for {result.code_raw}"
            return "Last scan: no code extracted"
        name = result.info.name or result.label or "Unknown"
        return f"Last scan: {name} ({result.label})"

    def _badge_style(self, value: str) -> str:
        color = "#2f8f4a"
        if "Hidden" in value or "Inactive" in value:
            color = "#9a2f2f"
        elif "Waiting" in value:
            color = "#2f85b5"
        return f"background-color: {color}; color: white; padding: 4px; border-radius: 4px;"
