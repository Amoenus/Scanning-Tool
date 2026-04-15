from dataclasses import dataclass, field
from typing import Optional

import tkinter as tk

from scanning_tool.domain.models import CaptureOverlayLayout, InfoOverlayGeometry

@dataclass
class OverlayState:
    # Capture overlay
    capture_overlay_root: Optional[tk.Toplevel] = None
    capture_overlay_canvas: Optional[tk.Canvas] = None
    capture_rect_id: Optional[int] = None
    capture_overlay_animation_job: Optional[str] = None
    capture_overlay_last_layout: Optional[CaptureOverlayLayout] = None

    # Info overlay
    info_overlay_root: Optional[tk.Toplevel] = None
    info_overlay_canvas: Optional[tk.Canvas] = None
    info_text_id: Optional[int] = None
    info_overlay_geometry: InfoOverlayGeometry = field(default_factory=InfoOverlayGeometry)
    overlay_text: str = ""
    last_overlay_time: float = 0

    # Anchor overlay
    anchor_overlay_root: Optional[tk.Toplevel] = None
    anchor_overlay_canvas: Optional[tk.Canvas] = None
    anchor_rect_id: Optional[int] = None
    anchor_overlay_visible: bool = True

    border_canvas: Optional[tk.Canvas] = None
    show_border: bool = True
