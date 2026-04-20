"""Runtime state manager for the scanning tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from scanning_tool.state.app_state import AppState

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.gui.control_state import ControlState

_app_state_target: AppState | None = None
_config_target: "ConfigData" | None = None
_config_service_target: "ConfigSaver" | None = None
_scan_state_target: "ScanState" | None = None
_service_state_target: "ServiceState" | None = None
_overlay_state_target: "OverlayState" | None = None
_control_state_target: "ControlState" | None = None


class _RuntimeProxy:
    __slots__ = ("_getter", "_name")

    def __init__(self, getter: Callable[[], Any], name: str) -> None:
        object.__setattr__(self, "_getter", getter)
        object.__setattr__(self, "_name", name)

    def _target(self) -> Any:
        target = self._getter()
        if target is None:
            raise RuntimeError(f"{self._name} has not been initialized")
        return target

    def __getattr__(self, item: str) -> Any:
        return getattr(self._target(), item)

    def __setattr__(self, item: str, value: Any) -> None:
        if item in {"_getter", "_name"}:
            object.__setattr__(self, item, value)
        else:
            setattr(self._target(), item, value)

    def __bool__(self) -> bool:
        return self._getter() is not None

    def __repr__(self) -> str:
        target = self._getter()
        state = "initialized" if target is not None else "uninitialized"
        return f"<{self._name} proxy ({state})>"


app_state = _RuntimeProxy(lambda: _app_state_target, "AppState")
config = _RuntimeProxy(lambda: _config_target, "ConfigData")
config_service = _RuntimeProxy(lambda: _config_service_target, "ConfigSaver")
scan_state = _RuntimeProxy(lambda: _scan_state_target, "ScanState")
service_state = _RuntimeProxy(lambda: _service_state_target, "ServiceState")
overlay_state = _RuntimeProxy(lambda: _overlay_state_target, "OverlayState")
control_state = _RuntimeProxy(lambda: _control_state_target, "ControlState")

__all__ = [
    "app_state",
    "config",
    "config_service",
    "scan_state",
    "service_state",
    "overlay_state",
    "control_state",
    "initialize_state",
    "save_config",
]


def initialize_state(app_state_: AppState, config_service_: "ConfigSaver") -> None:
    """Initialize global runtime state from the bootstrapper."""
    global _app_state_target, _config_target, _config_service_target
    global _scan_state_target, _service_state_target, _overlay_state_target, _control_state_target

    if _app_state_target is not None:
        raise RuntimeError("Runtime state has already been initialized")

    _app_state_target = app_state_
    _config_service_target = config_service_
    _config_target = app_state_.config
    _scan_state_target = app_state_.scan_state
    _service_state_target = app_state_.service_state
    _overlay_state_target = app_state_.overlay_state
    _control_state_target = app_state_.control_state


def save_config() -> None:
    """Persist the current configuration."""
    if _config_service_target is None:
        raise RuntimeError("Config service is not initialized")
    _config_service_target.save()
