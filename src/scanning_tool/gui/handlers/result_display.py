from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.gui.overlays import reposition_info_overlay
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.context import ActionContext


def _handle_update_result_display_offset(
    payload: dict[str, object],
    ctx: ActionContext,
) -> None:
    offset = ctx.config.overlay_config.info_offset
    offset.x = int(payload.get("x", offset.x))
    offset.y = int(payload.get("y", offset.y))
    status_updated.send(None, message=f"Display offset updated: x={offset.x}, y={offset.y}")
    reposition_info_overlay(ctx.overlay_state, ctx.config.overlay_config)


RESULT_DISPLAY_ACTION_HANDLERS = {
    ConfigAction.UPDATE_RESULT_DISPLAY_OFFSET: _handle_update_result_display_offset,
}
