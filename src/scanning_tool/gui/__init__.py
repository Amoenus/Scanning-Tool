"""GUI provider package for the scanning tool."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = ["GuiProvider", "get_default_gui_provider", "sections"]


def __getattr__(name: str) -> Any:
    if name == "sections":
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    if name in {"GuiProvider", "get_default_gui_provider"}:
        module = importlib.import_module(f"{__name__}.provider")
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(
        list(globals().keys()) + ["sections", "GuiProvider", "get_default_gui_provider"],
    )
