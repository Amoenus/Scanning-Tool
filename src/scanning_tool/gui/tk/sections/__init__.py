"""GUI sections — each owns one LabelFrame and its widgets/callbacks."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "Section",
    "SectionContext",
    "CaptureRegionSection",
    "ControlsSection",
    "HeadSwaySection",
    "OllamaSection",
    "ResultDisplaySection",
]

_SECTION_MODULE_MAP = {
    "Section": "base",
    "SectionContext": "base",
    "CaptureRegionSection": "capture_region",
    "ControlsSection": "controls",
    "HeadSwaySection": "head_sway",
    "OllamaSection": "ollama",
    "ResultDisplaySection": "result_display",
}


def __getattr__(name: str) -> Any:
    module_name = _SECTION_MODULE_MAP.get(name)
    if module_name is not None:
        module = importlib.import_module(f"{__name__}.{module_name}")
        value = getattr(module, name)
        globals()[name] = value
        return value

    try:
        module = importlib.import_module(f"{__name__}.{name}")
    except ImportError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    globals()[name] = module
    return module


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_SECTION_MODULE_MAP.keys()))
