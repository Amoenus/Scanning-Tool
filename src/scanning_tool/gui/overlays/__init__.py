"""Overlay package API.

This module exposes backend-agnostic overlay helpers and lazily delegates to the default
Tk backend implementation. It avoids importing the Tk-specific package at import time
so non-Tk consumers can import the shared GUI API without pulling Tk into the GUI layer.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Optional

from scanning_tool.config.service import ConfigData
from scanning_tool.gui.overlay_state import OverlayState

__all__ = (
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


def _tk_overlays() -> Any:
    return import_module("scanning_tool.gui.tk.overlays")


def choose_label_color(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().choose_label_color(*args, **kwargs)


def create_overlay_window(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().create_overlay_window(*args, **kwargs)


def enforce_topmost(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().enforce_topmost(*args, **kwargs)


def hide_anchor_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().hide_anchor_overlay(*args, **kwargs)


def hide_capture_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().hide_capture_overlay(*args, **kwargs)


def hide_info_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().hide_info_overlay(*args, **kwargs)


def register_anchor_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().register_anchor_sliders(*args, **kwargs)


def register_capture_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().register_capture_sliders(*args, **kwargs)


def register_overlay_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().register_overlay_sliders(*args, **kwargs)


def reposition_info_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().reposition_info_overlay(*args, **kwargs)


def show_anchor_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().show_anchor_overlay(*args, **kwargs)


def show_capture_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().show_capture_overlay(*args, **kwargs)


def show_info_overlay(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().show_info_overlay(*args, **kwargs)


def start_label_timeout(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().start_label_timeout(*args, **kwargs)


def toggle_border(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().toggle_border(*args, **kwargs)


def start_capture_overlay_animation(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().start_capture_overlay_animation(*args, **kwargs)


def stop_capture_overlay_animation(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().stop_capture_overlay_animation(*args, **kwargs)


def sync_anchor_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().sync_anchor_sliders(*args, **kwargs)


def sync_capture_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().sync_capture_sliders(*args, **kwargs)


def sync_capture_sliders_callback(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().sync_capture_sliders_callback(*args, **kwargs)


def configure_capture_slider_sync(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().configure_capture_slider_sync(*args, **kwargs)


def sync_overlay_sliders(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().sync_overlay_sliders(*args, **kwargs)


def update_capture_overlay_region(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().update_capture_overlay_region(*args, **kwargs)


def update_overlay_label(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().update_overlay_label(*args, **kwargs)


def update_anchor_overlay_region(*args: Any, **kwargs: Any) -> Any:
    return _tk_overlays().update_anchor_overlay_region(*args, **kwargs)


def show_overlay(
    overlay_state: OverlayState,
    config: ConfigData,
    screen_width: int | None = None,
    screen_height: int | None = None,
) -> Any:
    return _tk_overlays().show_overlay(
        overlay_state,
        config,
        screen_width=screen_width,
        screen_height=screen_height,
    )


def update_overlay_region(overlay_state: OverlayState) -> Any:
    return _tk_overlays().update_overlay_region(overlay_state)


def destroy_all_overlays(overlay_state: OverlayState) -> Any:
    return _tk_overlays().destroy_all_overlays(overlay_state)
