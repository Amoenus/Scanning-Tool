"""Global hotkey service."""
from __future__ import annotations


import keyboard
from loguru import logger

from scanning_tool.gui.overlays import toggle_border
from scanning_tool.state import manager


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.services.capture_service import CaptureService
def hotkey_listener(capture_service: CaptureService) -> None:
    """Set up hotkey listeners with cross-platform error handling."""
    try:
        keyboard.add_hotkey("7", capture_service.capture_once)
        keyboard.add_hotkey("ctrl+7", capture_service.toggle_continuous)
        keyboard.add_hotkey("8", lambda: toggle_border(manager.overlay_state))
        logger.info(
            "Hotkeys registered: '7' for single scan, 'Ctrl+7' for continuous toggle, '8' for border toggle",
        )
        keyboard.wait()
    except Exception as e:
        logger.warning(f"Could not set up global hotkeys: {e}")
        logger.info("Note: Linux Support is being tested.")
