"""Shared application state exports."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scanning_tool.state.app_state import AppState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.state.manager import (
    app_state,
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    save_config,
)

if TYPE_CHECKING:
    from scanning_tool.state.scan_state import ScanState


def __getattr__(name: str) -> Any:
    if name == "ScanState":
        from scanning_tool.state.scan_state import ScanState

        return ScanState
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + ["ScanState"])

__all__ = [
    "AppState",
    "ScanState",
    "ServiceState",
    "app_state",
    "config",
    "scan_state",
    "service_state",
    "overlay_state",
    "control_state",
    "save_config",
]
