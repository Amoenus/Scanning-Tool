from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.gui.overlays import (
    hide_capture_overlay,
    show_capture_overlay,
    toggle_border,
    update_capture_overlay_region,
)
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.context import ActionContext


def _handle_update_capture_region(
    payload: dict[str, object],
    ctx: ActionContext,
) -> None:
    region = ctx.config.capture_region
    region.left = int(payload.get("left", region.left))
    region.top = int(payload.get("top", region.top))
    region.width = int(payload.get("width", region.width))
    region.height = int(payload.get("height", region.height))
    update_capture_overlay_region(ctx.overlay_state)
    status_updated.send(None, message=f"CAP_REGION updated: {region}")


def _handle_toggle_capture_box(
    payload: dict[str, object],
    ctx: ActionContext,
) -> None:
    visible = bool(payload.get("visible", False))
    if visible:
        show_capture_overlay(ctx.overlay_state, ctx.config.capture_region)
        status_updated.send(None, message="Capture box shown.")
    else:
        hide_capture_overlay(ctx.overlay_state)
        status_updated.send(None, message="Capture box hidden.")


def _handle_toggle_capture_border(
    payload: dict[str, object],
    ctx: ActionContext,
) -> None:
    toggle_border(ctx.overlay_state)
    status_updated.send(
        None,
        message=f"Capture border {'enabled' if ctx.overlay_state.show_border else 'disabled'}.",
    )


CAPTURE_ACTION_HANDLERS: dict[str, Handler] = {
    ConfigAction.UPDATE_CAPTURE_REGION: _handle_update_capture_region,
    ConfigAction.TOGGLE_CAPTURE_BOX: _handle_toggle_capture_box,
    ConfigAction.TOGGLE_CAPTURE_BORDER: _handle_toggle_capture_border,
}
