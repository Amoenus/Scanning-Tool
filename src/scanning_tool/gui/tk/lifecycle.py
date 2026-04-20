"""Window lifecycle / teardown for the GUI."""

from typing import Callable
import tkinter as tk

from .overlays import (
    destroy_all_overlays,
    stop_capture_overlay_animation,
)
from .overlay_state import OverlayState


def register_close_handler(
    root: tk.Tk,
    overlay_state: OverlayState,
    save_config: Callable[[], None],
) -> None:
    """Wire the root window's close button to a clean teardown sequence."""

    def on_close() -> None:
        stop_capture_overlay_animation()
        save_config()
        destroy_all_overlays()

        overlay_state.capture.reset()
        overlay_state.info.reset()
        overlay_state.anchor.reset()

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
