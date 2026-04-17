"""Slider registration and synchronization helpers for overlays."""

from loguru import logger
import tkinter as tk

from scanning_tool.gui.control_state import ScaleWidget
from scanning_tool.core.state_manager import (
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    save_config,
)
from .base import safe_tk


def register_capture_sliders(
    left: ScaleWidget, top: ScaleWidget, width: ScaleWidget, height: ScaleWidget
) -> None:
    control_state.capture.left = left
    control_state.capture.top = top
    control_state.capture.width = width
    control_state.capture.height = height


def register_anchor_sliders(
    left: ScaleWidget,
    top: ScaleWidget,
    width: ScaleWidget,
    height: ScaleWidget,
    offset_x: ScaleWidget,
    offset_y: ScaleWidget,
) -> None:
    control_state.anchor.left = left
    control_state.anchor.top = top
    control_state.anchor.width = width
    control_state.anchor.height = height
    control_state.anchor.offset_x = offset_x
    control_state.anchor.offset_y = offset_y


def register_overlay_sliders(offset_x: ScaleWidget, offset_y: ScaleWidget) -> None:
    control_state.overlay.offset_x = offset_x
    control_state.overlay.offset_y = offset_y


def sync_capture_sliders() -> None:
    widgets = control_state.capture
    if not widgets.left or control_state.syncing.capture:
        return

    capture_region = config.capture_region

    def _apply() -> None:
        if control_state.syncing.capture:
            return
        control_state.syncing.capture = True
        try:
            try:
                widgets.left.set(int(capture_region.left))
                widgets.top.set(int(capture_region.top))
                widgets.width.set(int(capture_region.width))
                widgets.height.set(int(capture_region.height))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.capture = False

    safe_tk(lambda: widgets.left.after(0, _apply))


def sync_anchor_sliders() -> None:
    widgets = control_state.anchor
    if not widgets.left or control_state.syncing.anchor:
        return

    anchor_region = config.anchor_template
    anchor_offset = config.anchor_offset

    def _apply() -> None:
        if control_state.syncing.anchor:
            return
        control_state.syncing.anchor = True
        try:
            try:
                widgets.left.set(int(anchor_region.left))
                widgets.top.set(int(anchor_region.top))
                widgets.width.set(int(anchor_region.width))
                widgets.height.set(int(anchor_region.height))
                widgets.offset_x.set(int(anchor_offset.x))
                widgets.offset_y.set(int(anchor_offset.y))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.anchor = False

    safe_tk(lambda: widgets.left.after(0, _apply))


def sync_overlay_sliders() -> None:
    widgets = control_state.overlay
    if not widgets.offset_x or control_state.syncing.overlay:
        return

    overlay_offset = config.overlay_config.info_offset

    def _apply() -> None:
        if control_state.syncing.overlay:
            return
        control_state.syncing.overlay = True
        try:
            try:
                widgets.offset_x.set(int(overlay_offset.x))
                widgets.offset_y.set(int(overlay_offset.y))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.overlay = False

    safe_tk(lambda: widgets.offset_x.after(0, _apply))
