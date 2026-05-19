from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from scanning_tool.gui.handlers.anchor import ANCHOR_ACTION_HANDLERS
from scanning_tool.gui.handlers.capture import CAPTURE_ACTION_HANDLERS
from scanning_tool.gui.handlers.controls import CONTROL_ACTION_HANDLERS
from scanning_tool.gui.handlers.mobile_overlay import MOBILE_OVERLAY_ACTION_HANDLERS
from scanning_tool.gui.handlers.ollama import OLLAMA_ACTION_HANDLERS
from scanning_tool.gui.handlers.result_display import RESULT_DISPLAY_ACTION_HANDLERS

from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.scan import ScanAction
from scanning_tool.state.actions.runtime import RuntimeAction

from scanning_tool.gui.action_context import ActionContext

Handler = Callable[
    [dict[str, Any], ActionContext],
    None,
]

ActionKeyType = ConfigAction | ScanAction | RuntimeAction | object

ACTION_HANDLERS: dict[ActionKeyType, Handler] = {}
ACTION_HANDLERS.update(CONTROL_ACTION_HANDLERS)  # type: ignore[arg-type]
ACTION_HANDLERS.update(MOBILE_OVERLAY_ACTION_HANDLERS)  # type: ignore[arg-type]
ACTION_HANDLERS.update(OLLAMA_ACTION_HANDLERS)  # type: ignore[arg-type]
ACTION_HANDLERS.update(ANCHOR_ACTION_HANDLERS)  # type: ignore[arg-type]
ACTION_HANDLERS.update(CAPTURE_ACTION_HANDLERS)  # type: ignore[arg-type]
ACTION_HANDLERS.update(RESULT_DISPLAY_ACTION_HANDLERS)  # type: ignore[arg-type]

__all__ = ["ACTION_HANDLERS", "Handler"]
