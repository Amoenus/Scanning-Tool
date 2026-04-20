"""GUI sections package wrapper for backwards compatibility."""

from __future__ import annotations

from scanning_tool.gui.tk.sections import (
    CaptureRegionSection,
    ControlsSection,
    HeadSwaySection,
    OllamaSection,
    ResultDisplaySection,
    Section,
    SectionContext,
)

__all__ = [
    "Section",
    "SectionContext",
    "CaptureRegionSection",
    "ControlsSection",
    "HeadSwaySection",
    "OllamaSection",
    "ResultDisplaySection",
]
