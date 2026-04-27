"""Window lifecycle / teardown for the GUI."""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from .overlays import (
    destroy_all_overlays,
    stop_capture_overlay_animation,
)

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver

    from .overlay_state import OverlayState
def register_close_handler(
    root: tk.Tk,
    overlay_state: OverlayState,
    config_service: ConfigSaver,
) -> None:
    """Wire the root window's close button to a clean teardown sequence."""

    def on_close() -> None:
        stop_capture_overlay_animation()
        config_service.save()
        destroy_all_overlays(overlay_state)

        overlay_state.capture.reset()
        overlay_state.info.reset()
        overlay_state.anchor.reset()

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
