from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from scanning_tool.gui.handlers.anchor import ANCHOR_ACTION_HANDLERS
from scanning_tool.gui.handlers.capture import CAPTURE_ACTION_HANDLERS
from scanning_tool.gui.handlers.controls import CONTROL_ACTION_HANDLERS
from scanning_tool.gui.handlers.mobile_overlay import MOBILE_OVERLAY_ACTION_HANDLERS
from scanning_tool.gui.handlers.ollama import OLLAMA_ACTION_HANDLERS
from scanning_tool.gui.handlers.result_display import RESULT_DISPLAY_ACTION_HANDLERS

if TYPE_CHECKING:
    from scanning_tool.state.actions import ConfigAction

from scanning_tool.gui.action_context import ActionContext
from scanning_tool.gui.actions import UiActionPayload

Handler = Callable[
    [UiActionPayload, ActionContext],
    None,
]


ACTION_HANDLERS: dict[object, Handler] = {
    **CONTROL_ACTION_HANDLERS,
    **MOBILE_OVERLAY_ACTION_HANDLERS,
    **OLLAMA_ACTION_HANDLERS,
    **ANCHOR_ACTION_HANDLERS,
    **CAPTURE_ACTION_HANDLERS,
    **RESULT_DISPLAY_ACTION_HANDLERS,
}

__all__ = ["ACTION_HANDLERS", "Handler"]
