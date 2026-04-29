from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.state.actions import ConfigAction
from scanning_tool.gui.overlays import (
    hide_capture_overlay,
    show_capture_overlay,
    toggle_border,
)
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.gui.state import OverlayState
    from scanning_tool.interfaces import CaptureController


def _handle_update_capture_region(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    region = config.capture_region
    region.left = int(payload.get("left", region.left))
    region.top = int(payload.get("top", region.top))
    region.width = int(payload.get("width", region.width))
    region.height = int(payload.get("height", region.height))
    status_updated.send(None, message=f"CAP_REGION updated: {region}")


def _handle_toggle_capture_box(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    visible = bool(payload.get("visible", False))
    if visible:
        show_capture_overlay(overlay_state, config.capture_region)
        status_updated.send(None, message="Capture box shown.")
    else:
        hide_capture_overlay(overlay_state)
        status_updated.send(None, message="Capture box hidden.")


def _handle_toggle_capture_border(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state: OverlayState,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    toggle_border(overlay_state)
    status_updated.send(
        None,
        message=f"Capture border {'enabled' if overlay_state.show_border else 'disabled'}.",
    )


CAPTURE_ACTION_HANDLERS: dict[str, Handler] = {
    ConfigAction.UPDATE_CAPTURE_REGION: _handle_update_capture_region,
    ConfigAction.TOGGLE_CAPTURE_BOX: _handle_toggle_capture_box,
    ConfigAction.TOGGLE_CAPTURE_BORDER: _handle_toggle_capture_border,
}
