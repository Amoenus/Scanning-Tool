"""Star Citizen Deposit Scanner - OCR-powered mining code reader."""

from __future__ import annotations

import importlib
import types
from typing import Any

__version__ = "1.0.0"


def __getattr__(name: str) -> Any:
    if name in {"main", "gui"}:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + ["main", "gui"])
