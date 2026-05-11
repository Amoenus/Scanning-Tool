"""Slider registration and synchronization helpers for overlays."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import TYPE_CHECKING

from scanning_tool.gui.tk.overlays.base import safe_tk

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import CaptureRegion
    from scanning_tool.domain.common import Offset2D
    from scanning_tool.gui.tk.control_state import ControlState, ScaleWidget


def register_capture_sliders(
    left: ScaleWidget,
    top: ScaleWidget,
    width: ScaleWidget,
    height: ScaleWidget,
    control_state: ControlState,
) -> None:
    """Register capture region slider widgets with control state.

    Parameters
    ----------
    left : ScaleWidget
        Slider widget for left position.
    top : ScaleWidget
        Slider widget for top position.
    width : ScaleWidget
        Slider widget for width.
    height : ScaleWidget
        Slider widget for height.
    control_state : ControlState
        Control state to register widgets with.

    """
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
    """Register anchor region slider widgets with control state.

    Parameters
    ----------
    left : ScaleWidget
        Slider widget for left position.
    top : ScaleWidget
        Slider widget for top position.
    width : ScaleWidget
        Slider widget for width.
    height : ScaleWidget
        Slider widget for height.
    offset_x : ScaleWidget
        Slider widget for x offset.
    offset_y : ScaleWidget
        Slider widget for y offset.
    control_state : ControlState
        Control state to register widgets with.

    """
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
    """Register overlay region slider widgets with control state.

    Parameters
    ----------
    offset_x : ScaleWidget
        Slider widget for x offset.
    offset_y : ScaleWidget
        Slider widget for y offset.
    control_state : ControlState
        Control state to register widgets with.

    """
    control_state.overlay.offset_x = offset_x
    control_state.overlay.offset_y = offset_y


_control_state: ControlState | None = None
_capture_region_getter: Callable[[], CaptureRegion] | None = None


def configure_capture_slider_sync(
    control_state: ControlState,
    capture_region_getter: Callable[[], CaptureRegion],
) -> None:
    """Configure the callback function for capture slider synchronization.

    Parameters
    ----------
    control_state : ControlState
        Control state to use for slider synchronization.
    capture_region_getter : Callable[[], CaptureRegion]
        Function to retrieve the current capture region.

    """
    global _control_state, _capture_region_getter
    _control_state = control_state
    _capture_region_getter = capture_region_getter


def sync_capture_sliders(
    control_state: ControlState,
    capture_region: CaptureRegion,
) -> None:
    """Synchronize capture slider widgets with capture region values.

    Parameters
    ----------
    control_state : ControlState
        Control state containing the slider widgets.
    capture_region : CaptureRegion
        Capture region with values to sync to sliders.

    """
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
    """Synchronize capture sliders using global configuration.

    Retrieves the current capture region and synchronizes the capture slider
    widgets with its values using the configured control state.

    """
    if _control_state is None or _capture_region_getter is None:
        return
    sync_capture_sliders(_control_state, _capture_region_getter())


def sync_anchor_sliders(
    control_state: ControlState,
    anchor_region: CaptureRegion,
    anchor_offset: Offset2D,
) -> None:
    """Synchronize anchor slider widgets with anchor region and offset values.

    Parameters
    ----------
    control_state : ControlState
        Control state containing the slider widgets.
    anchor_region : CaptureRegion
        Anchor region with values to sync to sliders.
    anchor_offset : Offset2D
        Anchor offset with values to sync to sliders.

    """
    widgets = control_state.anchor
    left = widgets.left
    top = widgets.top
    width = widgets.width
    height = widgets.height
    offset_x = widgets.offset_x
    offset_y = widgets.offset_y
    if not (left and top and width and height and offset_x and offset_y) or control_state.syncing.anchor:
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
