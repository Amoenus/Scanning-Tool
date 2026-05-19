from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.gui.overlays import (
    hide_capture_overlay,
    show_capture_overlay,
    toggle_border,
    update_capture_overlay_region,
)
from scanning_tool.gui.dtos import RegionPayloadDTO, TogglePayloadDTO
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.action_context import ActionContext

    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.gui.state import OverlayState
    from scanning_tool.interfaces import CaptureController


def _handle_update_capture_region(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    dto = RegionPayloadDTO.from_dict(payload)
    region = context.config.capture_region
    if dto.left is not None:
        region.left = dto.left
    if dto.top is not None:
        region.top = dto.top
    if dto.width is not None:
        region.width = dto.width
    if dto.height is not None:
        region.height = dto.height
    update_capture_overlay_region()
    status_updated.send(None, message=f"CAP_REGION updated: {region}")


def _handle_toggle_capture_box(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    dto = TogglePayloadDTO.from_dict(payload)
    visible = dto.visible if dto.visible is not None else False
    if visible:
        show_capture_overlay(context.overlay_state, context.config.capture_region)
        status_updated.send(None, message="Capture box shown.")
    else:
        hide_capture_overlay(context.overlay_state)
        status_updated.send(None, message="Capture box hidden.")


def _handle_toggle_capture_border(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    toggle_border(context.overlay_state)
    status_updated.send(
        None,
        message=f"Capture border {'enabled' if context.overlay_state.show_border else 'disabled'}.",
    )


CAPTURE_ACTION_HANDLERS = {
    ConfigAction.UPDATE_CAPTURE_REGION: _handle_update_capture_region,
    ConfigAction.TOGGLE_CAPTURE_BOX: _handle_toggle_capture_box,
    ConfigAction.TOGGLE_CAPTURE_BORDER: _handle_toggle_capture_border,
}
