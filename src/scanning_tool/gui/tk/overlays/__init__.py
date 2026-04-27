"""Overlay package API."""
from __future__ import annotations


from typing import Optional

from scanning_tool.gui.control_state import ControlState

from .anchor import (
    hide_anchor_overlay,
    show_anchor_overlay,
    update_anchor_overlay_region,
)
from .base import create_overlay_window, enforce_topmost, safe_tk
from .capture import (
    hide_capture_overlay,
    show_capture_overlay,
    start_capture_overlay_animation,
    stop_capture_overlay_animation,
    update_capture_overlay_region,
)
from .info import (
    choose_label_color,
    hide_info_overlay,
    reposition_info_overlay,
    show_info_overlay,
    start_label_timeout,
    toggle_border,
    update_overlay_label,
)
from .slider_sync import (
    configure_capture_slider_sync,
    register_anchor_sliders,
    register_capture_sliders,
    register_overlay_sliders,
    sync_anchor_sliders,
    sync_capture_sliders,
    sync_capture_sliders_callback,
    sync_overlay_sliders,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.config.service import ConfigData
__all__ = (
    "ControlState",
    "choose_label_color",
    "configure_capture_slider_sync",
    "create_overlay_window",
    "destroy_all_overlays",
    "enforce_topmost",
    "hide_anchor_overlay",
    "hide_capture_overlay",
    "hide_info_overlay",
    "register_anchor_sliders",
    "register_capture_sliders",
    "register_overlay_sliders",
    "reposition_info_overlay",
    "show_anchor_overlay",
    "show_capture_overlay",
    "show_info_overlay",
    "show_overlay",
    "start_capture_overlay_animation",
    "start_label_timeout",
    "stop_capture_overlay_animation",
    "sync_anchor_sliders",
    "sync_capture_sliders",
    "sync_capture_sliders_callback",
    "sync_overlay_sliders",
    "toggle_border",
    "update_anchor_overlay_region",
    "update_capture_overlay_region",
    "update_overlay_label",
    "update_overlay_region",
)


def show_overlay(
    overlay_state: OverlayState,
    config: ConfigData,
    screen_width: int | None = None,
    screen_height: int | None = None,
) -> None:
    show_anchor_overlay(overlay_state, config.anchor_template)
    show_capture_overlay(overlay_state, config.capture_region)

    if screen_width is None or screen_height is None:
        if overlay_state.capture_overlay_root and safe_tk(
            overlay_state.capture_overlay_root.winfo_exists, False,
        ):
            screen_width = (
                safe_tk(overlay_state.capture_overlay_root.winfo_screenwidth, 1920)
                or 1920
            )
            screen_height = (
                safe_tk(overlay_state.capture_overlay_root.winfo_screenheight, 1080)
                or 1080
            )

    if screen_width is not None and screen_height is not None:
        show_info_overlay(
            screen_width,
            screen_height,
            overlay_state,
            config.overlay_config,
        )


def update_overlay_region(overlay_state: OverlayState) -> None:
    update_anchor_overlay_region(overlay_state)
    update_capture_overlay_region()


def destroy_all_overlays(overlay_state: OverlayState) -> None:
    hide_anchor_overlay(overlay_state)
    hide_capture_overlay(overlay_state)
    hide_info_overlay(overlay_state)
