"""Runtime state manager for the scanning tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.state.app_state import AppState
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


@dataclass(frozen=True)
class _RuntimeState:
    app_state: AppState
    config: ConfigData
    config_service: ConfigSaver
    scan_state: ScanState
    service_state: ServiceState
    overlay_state: OverlayState
    control_state: ControlState


_runtime_state: _RuntimeState | None = None

app_state: AppState = cast("AppState", None)
config: ConfigData = cast("ConfigData", None)
config_service: ConfigSaver = cast("ConfigSaver", None)
scan_state: ScanState = cast("ScanState", None)
service_state: ServiceState = cast("ServiceState", None)
overlay_state: OverlayState = cast("OverlayState", None)
control_state: ControlState = cast("ControlState", None)

__all__ = [
    "app_state",
    "config",
    "config_service",
    "control_state",
    "initialize_state",
    "overlay_state",
    "save_config",
    "scan_state",
    "service_state",
]


def _assert_uninitialized() -> None:
    if _runtime_state is not None:
        message = "Runtime state has already been initialized"
        raise RuntimeError(message)


def _get_config_service() -> ConfigSaver:
    if _runtime_state is None:
        message = "Config service is not initialized"
        raise RuntimeError(message)
    return _runtime_state.config_service


def initialize_state(app_state_: AppState, config_service_: ConfigSaver) -> None:
    """Initialize global runtime state from the bootstrapper."""
    _assert_uninitialized()

    state = _RuntimeState(
        app_state=app_state_,
        config=app_state_.config,
        config_service=config_service_,
        scan_state=app_state_.scan_state,
        service_state=app_state_.service_state,
        overlay_state=app_state_.overlay_state,
        control_state=app_state_.control_state,
    )

    globals().update(
        {
            "app_state": state.app_state,
            "config": state.config,
            "config_service": state.config_service,
            "scan_state": state.scan_state,
            "service_state": state.service_state,
            "overlay_state": state.overlay_state,
            "control_state": state.control_state,
        },
    )
    globals()["_runtime_state"] = state


def save_config() -> None:
    """Persist the current configuration."""
    _get_config_service().save()
