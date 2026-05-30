"""Action handlers for result_display."""
from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.gui.handlers.payloads import OffsetUpdatePayload
from scanning_tool.gui.overlays import reposition_info_overlay
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.action_context import ActionContext
    from scanning_tool.gui.handlers import Handler


def _handle_update_result_display_offset(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    offset = context.config.overlay_config.info_offset
    data = OffsetUpdatePayload.model_validate(payload)
    if data.x is not None:
        offset.x = data.x
    if data.y is not None:
        offset.y = data.y
    status_updated.send(None, message=f"Display offset updated: x={offset.x}, y={offset.y}")
    reposition_info_overlay(context.overlay_state, context.config.overlay_config)


RESULT_DISPLAY_ACTION_HANDLERS: dict[object, Handler] = {
    ConfigAction.UPDATE_RESULT_DISPLAY_OFFSET: _handle_update_result_display_offset,
}
