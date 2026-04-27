"""Runtime state manager for the scanning tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from scanning_tool.config.service import ConfigData, ConfigSaver
from scanning_tool.gui.control_state import ControlState
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.state.app_state import AppState
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
_app_state_target: AppState | None = None
_config_target: ConfigData | None = None
_config_service_target: ConfigSaver | None = None
_scan_state_target: ScanState | None = None
_service_state_target: ServiceState | None = None
_overlay_state_target: OverlayState | None = None
_control_state_target: ControlState | None = None

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


def initialize_state(app_state_: AppState, config_service_: ConfigSaver) -> None:
    """Initialize global runtime state from the bootstrapper."""
    global _app_state_target, _config_target, _config_service_target
    global \
        _scan_state_target, \
        _service_state_target, \
        _overlay_state_target, \
        _control_state_target
    global \
        app_state, \
        config, \
        config_service, \
        scan_state, \
        service_state, \
        overlay_state, \
        control_state

    if _app_state_target is not None:
        raise RuntimeError("Runtime state has already been initialized")

    _app_state_target = app_state_
    _config_service_target = config_service_
    _config_target = app_state_.config
    _scan_state_target = app_state_.scan_state
    _service_state_target = app_state_.service_state
    _overlay_state_target = app_state_.overlay_state
    _control_state_target = app_state_.control_state

    app_state = app_state_
    config_service = config_service_
    config = app_state_.config
    scan_state = app_state_.scan_state
    service_state = app_state_.service_state
    overlay_state = app_state_.overlay_state
    control_state = app_state_.control_state


def save_config() -> None:
    """Persist the current configuration."""
    if _config_service_target is None:
        raise RuntimeError("Config service is not initialized")
    _config_service_target.save()
