from dataclasses import dataclass, field
from typing import Optional

import tkinter as tk

from scanning_tool.domain.models import CaptureOverlayLayout, InfoOverlayGeometry


@dataclass
class CaptureOverlayState:
    """State for the capture region overlay."""

    root: Optional[tk.Toplevel] = None
    canvas: Optional[tk.Canvas] = None
    rect_id: Optional[int] = None
    animation_job: Optional[str] = None
    last_layout: Optional[CaptureOverlayLayout] = None

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.rect_id = None


@dataclass
class InfoOverlayState:
    """State for the info/label overlay."""

    root: Optional[tk.Toplevel] = None
    canvas: Optional[tk.Canvas] = None
    text_id: Optional[int] = None
    geometry: InfoOverlayGeometry = field(default_factory=InfoOverlayGeometry)
    overlay_text: str = ""
    last_overlay_time: float = 0

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.text_id = None


@dataclass
class AnchorOverlayState:
    """State for the anchor template overlay."""

    root: Optional[tk.Toplevel] = None
    canvas: Optional[tk.Canvas] = None
    rect_id: Optional[int] = None
    visible: bool = True

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.rect_id = None


@dataclass
class OverlayState:
    capture: CaptureOverlayState = field(default_factory=CaptureOverlayState)
    info: InfoOverlayState = field(default_factory=InfoOverlayState)
    anchor: AnchorOverlayState = field(default_factory=AnchorOverlayState)

    border_canvas: Optional[tk.Canvas] = None
    show_border: bool = True

    # --- Backward-compatible property accessors ---
    # These keep existing code working while consumers migrate to the sub-state API.

    @property
    def capture_overlay_root(self) -> Optional[tk.Toplevel]:
        return self.capture.root

    @capture_overlay_root.setter
    def capture_overlay_root(self, value: Optional[tk.Toplevel]) -> None:
        self.capture.root = value

    @property
    def capture_overlay_canvas(self) -> Optional[tk.Canvas]:
        return self.capture.canvas

    @capture_overlay_canvas.setter
    def capture_overlay_canvas(self, value: Optional[tk.Canvas]) -> None:
        self.capture.canvas = value

    @property
    def capture_rect_id(self) -> Optional[int]:
        return self.capture.rect_id

    @capture_rect_id.setter
    def capture_rect_id(self, value: Optional[int]) -> None:
        self.capture.rect_id = value

    @property
    def capture_overlay_animation_job(self) -> Optional[str]:
        return self.capture.animation_job

    @capture_overlay_animation_job.setter
    def capture_overlay_animation_job(self, value: Optional[str]) -> None:
        self.capture.animation_job = value

    @property
    def capture_overlay_last_layout(self) -> Optional[CaptureOverlayLayout]:
        return self.capture.last_layout

    @capture_overlay_last_layout.setter
    def capture_overlay_last_layout(
        self, value: Optional[CaptureOverlayLayout]
    ) -> None:
        self.capture.last_layout = value

    @property
    def info_overlay_root(self) -> Optional[tk.Toplevel]:
        return self.info.root

    @info_overlay_root.setter
    def info_overlay_root(self, value: Optional[tk.Toplevel]) -> None:
        self.info.root = value

    @property
    def info_overlay_canvas(self) -> Optional[tk.Canvas]:
        return self.info.canvas

    @info_overlay_canvas.setter
    def info_overlay_canvas(self, value: Optional[tk.Canvas]) -> None:
        self.info.canvas = value

    @property
    def info_text_id(self) -> Optional[int]:
        return self.info.text_id

    @info_text_id.setter
    def info_text_id(self, value: Optional[int]) -> None:
        self.info.text_id = value

    @property
    def info_overlay_geometry(self) -> InfoOverlayGeometry:
        return self.info.geometry

    @info_overlay_geometry.setter
    def info_overlay_geometry(self, value: InfoOverlayGeometry) -> None:
        self.info.geometry = value

    @property
    def overlay_text(self) -> str:
        return self.info.overlay_text

    @overlay_text.setter
    def overlay_text(self, value: str) -> None:
        self.info.overlay_text = value

    @property
    def last_overlay_time(self) -> float:
        return self.info.last_overlay_time

    @last_overlay_time.setter
    def last_overlay_time(self, value: float) -> None:
        self.info.last_overlay_time = value

    @property
    def anchor_overlay_root(self) -> Optional[tk.Toplevel]:
        return self.anchor.root

    @anchor_overlay_root.setter
    def anchor_overlay_root(self, value: Optional[tk.Toplevel]) -> None:
        self.anchor.root = value

    @property
    def anchor_overlay_canvas(self) -> Optional[tk.Canvas]:
        return self.anchor.canvas

    @anchor_overlay_canvas.setter
    def anchor_overlay_canvas(self, value: Optional[tk.Canvas]) -> None:
        self.anchor.canvas = value

    @property
    def anchor_rect_id(self) -> Optional[int]:
        return self.anchor.rect_id

    @anchor_rect_id.setter
    def anchor_rect_id(self, value: Optional[int]) -> None:
        self.anchor.rect_id = value

    @property
    def anchor_overlay_visible(self) -> bool:
        return self.anchor.visible

    @anchor_overlay_visible.setter
    def anchor_overlay_visible(self, value: bool) -> None:
        self.anchor.visible = value
