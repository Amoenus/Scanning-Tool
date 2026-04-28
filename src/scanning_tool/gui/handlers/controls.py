from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.interfaces import CaptureController


def _handle_single_scan(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    Thread(target=capture_service.capture_once, daemon=True).start()
    status_updated.send(None, message="Single scan requested.")


def _handle_toggle_continuous_capture(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    capture_service.toggle_continuous()
    status_updated.send(None, message="Toggled continuous capture mode.")


def _handle_update_continuous_capture_interval(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    value = float(payload.get("value", config.continuous_capture_interval))
    config.continuous_capture_interval = value
    status_updated.send(None, message=f"Continuous capture interval set to {value:.1f}s")


def _handle_save_config(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    config_service.save()
    status_updated.send(None, message="Configuration saved.")


CONTROL_ACTION_HANDLERS = {
    UiActionType.SINGLE_SCAN: _handle_single_scan,
    UiActionType.TOGGLE_CONTINUOUS_CAPTURE: _handle_toggle_continuous_capture,
    UiActionType.UPDATE_CONTINUOUS_CAPTURE_INTERVAL: _handle_update_continuous_capture_interval,
    UiActionType.SAVE_CONFIG: _handle_save_config,
}
