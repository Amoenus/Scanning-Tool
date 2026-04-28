"""Advanced settings section — collapsible container for configuration controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from .capture_region import CaptureRegionSection
from .head_sway import HeadSwaySection
from .ollama import OllamaSection
from .result_display import ResultDisplaySection
from ..widgets import create_button_row

if TYPE_CHECKING:
    from .base import SectionContext


class SettingsSection:
    """Holds advanced configuration sections behind an expandable container."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Advanced Settings", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._expanded = False
        self._toggle_text = tk.StringVar(value="Show advanced settings")

        create_button_row(
            frame,
            [
                (self._toggle_text, self._toggle_visibility),
            ],
        )

        self._settings_container = ttk.Frame(frame, style="Glass.Section.TFrame")
        self._build_hidden_sections()
        return frame

    def _build_hidden_sections(self) -> None:
        CaptureRegionSection().build(self._settings_container, self._ctx)
        HeadSwaySection().build(self._settings_container, self._ctx)
        OllamaSection().build(self._settings_container, self._ctx)
        ResultDisplaySection().build(self._settings_container, self._ctx)

    def _toggle_visibility(self) -> None:
        self._expanded = not self._expanded
        if self._expanded:
            self._settings_container.pack(fill="x", padx=(5, 0), pady=(8, 0))
            self._toggle_text.set("Hide advanced settings")
        else:
            self._settings_container.pack_forget()
            self._toggle_text.set("Show advanced settings")
