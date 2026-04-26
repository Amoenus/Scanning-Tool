"""Slider registration and synchronization helpers for overlays."""

import tkinter as tk
from typing import Callable

from ..control_state import ControlState, ScaleWidget
from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.domain.common import Offset2D
from .base import safe_tk


def register_capture_sliders(
    left: ScaleWidget,
    top: ScaleWidget,
    width: ScaleWidget,
    height: ScaleWidget,
    control_state: ControlState,
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
    control_state: ControlState,
) -> None:
    control_state.anchor.left = left
    control_state.anchor.top = top
    control_state.anchor.width = width
    control_state.anchor.height = height
    control_state.anchor.offset_x = offset_x
    control_state.anchor.offset_y = offset_y


def register_overlay_sliders(
    offset_x: ScaleWidget,
    offset_y: ScaleWidget,
    control_state: ControlState,
) -> None:
    control_state.overlay.offset_x = offset_x
    control_state.overlay.offset_y = offset_y


_control_state: ControlState | None = None
_capture_region_getter: Callable[[], CaptureRegion] | None = None


def configure_capture_slider_sync(
    control_state: ControlState,
    capture_region_getter: Callable[[], CaptureRegion],
) -> None:
    global _control_state, _capture_region_getter
    _control_state = control_state
    _capture_region_getter = capture_region_getter


def sync_capture_sliders(
    control_state: ControlState, capture_region: CaptureRegion
) -> None:
    widgets = control_state.capture
    left = widgets.left
    top = widgets.top
    width = widgets.width
    height = widgets.height
    if not (left and top and width and height) or control_state.syncing.capture:
        return

    def _apply() -> None:
        if control_state.syncing.capture:
            return
        control_state.syncing.capture = True
        try:
            try:
                left.set(int(capture_region.left))
                top.set(int(capture_region.top))
                width.set(int(capture_region.width))
                height.set(int(capture_region.height))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.capture = False

    safe_tk(lambda: left.after(0, _apply))


def sync_capture_sliders_callback() -> None:
    if _control_state is None or _capture_region_getter is None:
        return
    sync_capture_sliders(_control_state, _capture_region_getter())


def sync_anchor_sliders(
    control_state: ControlState,
    anchor_region: CaptureRegion,
    anchor_offset: Offset2D,
) -> None:
    widgets = control_state.anchor
    left = widgets.left
    top = widgets.top
    width = widgets.width
    height = widgets.height
    offset_x = widgets.offset_x
    offset_y = widgets.offset_y
    if (
        not (left and top and width and height and offset_x and offset_y)
        or control_state.syncing.anchor
    ):
        return

    def _apply() -> None:
        if control_state.syncing.anchor:
            return
        control_state.syncing.anchor = True
        try:
            try:
                left.set(int(anchor_region.left))
                top.set(int(anchor_region.top))
                width.set(int(anchor_region.width))
                height.set(int(anchor_region.height))
                offset_x.set(int(anchor_offset.x))
                offset_y.set(int(anchor_offset.y))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.anchor = False

    safe_tk(lambda: left.after(0, _apply))


def sync_overlay_sliders(
    control_state: ControlState,
    overlay_offset: Offset2D,
) -> None:
    widgets = control_state.overlay
    offset_x = widgets.offset_x
    offset_y = widgets.offset_y
    if not (offset_x and offset_y) or control_state.syncing.overlay:
        return

    def _apply() -> None:
        if control_state.syncing.overlay:
            return
        control_state.syncing.overlay = True
        try:
            try:
                offset_x.set(int(overlay_offset.x))
                offset_y.set(int(overlay_offset.y))
            except tk.TclError:
                pass
        finally:
            control_state.syncing.overlay = False

    safe_tk(lambda: offset_x.after(0, _apply))
