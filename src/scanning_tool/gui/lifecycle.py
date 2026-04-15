"""Window lifecycle / teardown for the GUI."""

import tkinter as tk

from scanning_tool.gui.overlays import destroy_all_overlays, stop_capture_overlay_animation
from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config


def register_close_handler(root: tk.Tk) -> None:
    """Wire the root window's close button to a clean teardown sequence."""

    def on_close() -> None:
        stop_capture_overlay_animation()
        save_config()
        destroy_all_overlays()

        overlay_state.capture_overlay_root = None
        overlay_state.capture_overlay_canvas = None
        overlay_state.capture_rect_id = None
        overlay_state.anchor_overlay_root = None
        overlay_state.anchor_overlay_canvas = None
        overlay_state.anchor_rect_id = None
        overlay_state.info_overlay_root = None
        overlay_state.info_overlay_canvas = None
        overlay_state.info_text_id = None

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
