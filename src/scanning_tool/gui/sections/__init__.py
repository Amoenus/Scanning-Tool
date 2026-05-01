"""GUI sections package wrapper for backwards compatibility."""

from __future__ import annotations

import importlib
from typing import Any

from scanning_tool.gui.tk.sections import (
    CaptureRegionSection,
    ControlsSection,
    HeadSwaySection,
    MobileOverlaySection,
    OllamaSection,
    ResultDisplaySection,
    Section,
    SectionContext,
    StatusOverviewSection,
)

__all__ = [
    "CaptureRegionSection",
    "ControlsSection",
    "HeadSwaySection",
    "MobileOverlaySection",
    "OllamaSection",
    "ResultDisplaySection",
    "Section",
    "SectionContext",
    "StatusOverviewSection",
]

_SECTION_MODULE_MAP = {
    "mobile_overlay": "scanning_tool.gui.tk.sections.mobile_overlay",
    "ollama": "scanning_tool.gui.tk.sections.ollama",
}


def __getattr__(name: str) -> Any:
    if name in _SECTION_MODULE_MAP:
        module = importlib.import_module(_SECTION_MODULE_MAP[name])
        globals()[name] = module
        return module
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_SECTION_MODULE_MAP.keys()))
