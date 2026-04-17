"""Tkinter GUI package for the scanning tool."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = ["sections"]


def __getattr__(name: str) -> Any:
    if name == "sections":
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + ["sections"])
