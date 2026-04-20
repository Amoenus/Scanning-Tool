"""Shared GUI layout datatypes for backend-agnostic UI logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InfoOverlayGeometry:
    """Geometry snapshot for the info overlay window."""

    screen_width: int | None = None
    screen_height: int | None = None
    width: int = 0
    height: int = 0


@dataclass
class CaptureOverlayLayout:
    """Layout values for positioning and sizing the capture overlay."""

    overlay_width: int
    overlay_height: int
    left: int
    top: int
    padding_x: int
    padding_y: int
    cap_w: int
    cap_h: int


@dataclass
class AnchorOverlayGeometry:
    """Geometry for the anchor overlay window."""

    width: int
    height: int
    left: int
    top: int


@dataclass
class InfoOverlayLayout:
    """Computed position and size for the floating info overlay."""

    width: int
    height: int
    left: int
    top: int
