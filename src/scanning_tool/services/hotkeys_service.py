"""Global hotkey service."""
from __future__ import annotations

from typing import TYPE_CHECKING

import keyboard
from loguru import logger

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.overlays import toggle_border
from scanning_tool.services.edit_mode_service import edit_mode_service
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.signals.edit_mode import edit_mode_changed
from scanning_tool.state import manager

if TYPE_CHECKING:
    from scanning_tool.services.capture_service import CaptureService
_edit_mode_hotkeys: list[str] = []


def _register_edit_mode_hotkeys() -> None:
    global _edit_mode_hotkeys
    if _edit_mode_hotkeys:
        return
    handles: list[str] = []
    handles.append(keyboard.add_hotkey("tab", lambda: publish_ui_action(EditModeAction.CYCLE_REGION), suppress=True))
    handles.append(keyboard.add_hotkey("left", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": -1}), suppress=True))
    handles.append(keyboard.add_hotkey("right", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": 1}), suppress=True))
    handles.append(keyboard.add_hotkey("up", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": -1}), suppress=True))
    handles.append(keyboard.add_hotkey("down", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": 1}), suppress=True))
    handles.append(keyboard.add_hotkey("shift+left", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": -10}), suppress=True))
    handles.append(keyboard.add_hotkey("shift+right", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": 10}), suppress=True))
    handles.append(keyboard.add_hotkey("shift+up", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": -10}), suppress=True))
    handles.append(keyboard.add_hotkey("shift+down", lambda: publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": 10}), suppress=True))
    handles.append(keyboard.add_hotkey("esc", lambda: publish_ui_action(EditModeAction.EXIT_EDIT_MODE), suppress=True))
    _edit_mode_hotkeys = handles


def _unregister_edit_mode_hotkeys() -> None:
    global _edit_mode_hotkeys
    for handle in _edit_mode_hotkeys:
        try:
            keyboard.remove_hotkey(handle)
        except Exception:
            pass
    _edit_mode_hotkeys = []


def _on_edit_mode_changed(sender: object, state=None, **kwargs: object) -> None:
    if state and getattr(state, "is_edit_mode", False):
        _register_edit_mode_hotkeys()
    else:
        _unregister_edit_mode_hotkeys()


def hotkey_listener(capture_service: CaptureService) -> None:
    """Set up hotkey listeners with cross-platform error handling."""
    try:
        keyboard.add_hotkey("7", capture_service.capture_once)
        keyboard.add_hotkey("ctrl+7", capture_service.toggle_continuous)
        keyboard.add_hotkey("8", lambda: toggle_border(manager.overlay_state))
        keyboard.add_hotkey("f9", lambda: publish_ui_action(
            EditModeAction.EXIT_EDIT_MODE if edit_mode_service.state.is_edit_mode else EditModeAction.ENTER_EDIT_MODE,
        ))
        edit_mode_changed.connect(_on_edit_mode_changed, weak=False)
        logger.info(
            "Hotkeys registered: '7' for single scan, 'Ctrl+7' for continuous toggle, '8' for border toggle, 'F9' for edit mode",
        )
        keyboard.wait()
    except Exception as e:
        logger.warning(f"Could not set up global hotkeys: {e}")
        logger.info("Note: Linux Support is being tested.")
