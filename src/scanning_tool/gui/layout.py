"""Tkinter GUI wrapper module for backwards compatibility."""

from __future__ import annotations

from scanning_tool.gui.tk.layout import (
    AnchorOverlayGeometry,
    CaptureOverlayLayout,
    InfoOverlayGeometry,
    InfoOverlayLayout,
)

__all__ = [
    "CaptureOverlayLayout",
    "InfoOverlayGeometry",
    "InfoOverlayLayout",
    "AnchorOverlayGeometry",
]
