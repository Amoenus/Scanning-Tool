"""Shared GUI state models for backend-agnostic UI support."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from blinker import Signal

from scanning_tool.gui.layout_types import CaptureOverlayLayout, InfoOverlayGeometry

ScaleWidget = Any
OverlayCaptureRootListener = Callable[[Any | None], None]


@dataclass
class CaptureSliders:
    """Slider widgets for the capture region controls."""

    left: ScaleWidget | None = None
    top: ScaleWidget | None = None
    width: ScaleWidget | None = None
    height: ScaleWidget | None = None


@dataclass
class AnchorSliders:
    """Slider widgets for the anchor region and offset controls."""

    left: ScaleWidget | None = None
    top: ScaleWidget | None = None
    width: ScaleWidget | None = None
    height: ScaleWidget | None = None
    offset_x: ScaleWidget | None = None
    offset_y: ScaleWidget | None = None


@dataclass
class OverlaySliders:
    """Slider widgets for the info overlay offset controls."""

    offset_x: ScaleWidget | None = None
    offset_y: ScaleWidget | None = None


@dataclass
class SyncFlags:
    """Prevents re-entrant slider updates during programmatic changes."""

    capture: bool = False
    anchor: bool = False
    overlay: bool = False


@dataclass
class ControlState:
    """Typed registry for GUI slider widgets and sync guards."""

    capture: CaptureSliders = field(default_factory=CaptureSliders)
    anchor: AnchorSliders = field(default_factory=AnchorSliders)
    overlay: OverlaySliders = field(default_factory=OverlaySliders)
    syncing: SyncFlags = field(default_factory=SyncFlags)


@dataclass
class CaptureOverlayState:
    """State for the capture region overlay."""

    root: Any | None = None
    canvas: Any | None = None
    rect_id: int | None = None
    animation_job: str | None = None
    last_layout: CaptureOverlayLayout | None = None

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.rect_id = None
        self.animation_job = None
        self.last_layout = None


@dataclass
class InfoOverlayState:
    """State for the info/label overlay."""

    root: Any | None = None
    canvas: Any | None = None
    text_id: int | None = None
    geometry: InfoOverlayGeometry = field(default_factory=InfoOverlayGeometry)
    overlay_text: str = ""
    last_overlay_time: float = 0.0

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.text_id = None


@dataclass
class AnchorOverlayState:
    """State for the anchor template overlay."""

    root: Any | None = None
    canvas: Any | None = None
    rect_id: int | None = None
    visible: bool = True

    def reset(self) -> None:
        """Null all references for teardown."""
        self.root = None
        self.canvas = None
        self.rect_id = None


@dataclass
class OverlayState:
    """Shared overlay state for any GUI backend."""

    capture: CaptureOverlayState = field(default_factory=CaptureOverlayState)
    info: InfoOverlayState = field(default_factory=InfoOverlayState)
    anchor: AnchorOverlayState = field(default_factory=AnchorOverlayState)
    border_canvas: Any | None = None
    show_border: bool = True

    _capture_overlay_root_signal: Signal = field(
        default_factory=Signal, init=False, repr=False,
    )

    @property
    def capture_overlay_root(self) -> Any | None:
        return self.capture.root

    @capture_overlay_root.setter
    def capture_overlay_root(self, value: Any | None) -> None:
        if self.capture.root is value:
            return
        self.capture.root = value
        self._notify_capture_overlay_root_listeners()

    def add_capture_overlay_root_listener(
        self,
        listener: OverlayCaptureRootListener,
    ) -> None:
        def receiver(sender: object, capture_root: Any | None) -> None:
            listener(capture_root)

        self._capture_overlay_root_signal.connect(receiver, weak=False)

    def _notify_capture_overlay_root_listeners(self) -> None:
        self._capture_overlay_root_signal.send(self, capture_root=self.capture.root)

    @property
    def capture_overlay_canvas(self) -> Any | None:
        return self.capture.canvas

    @capture_overlay_canvas.setter
    def capture_overlay_canvas(self, value: Any | None) -> None:
        self.capture.canvas = value

    @property
    def capture_rect_id(self) -> int | None:
        return self.capture.rect_id

    @capture_rect_id.setter
    def capture_rect_id(self, value: int | None) -> None:
        self.capture.rect_id = value

    @property
    def capture_overlay_animation_job(self) -> str | None:
        return self.capture.animation_job

    @capture_overlay_animation_job.setter
    def capture_overlay_animation_job(self, value: str | None) -> None:
        self.capture.animation_job = value

    @property
    def capture_overlay_last_layout(self) -> CaptureOverlayLayout | None:
        return self.capture.last_layout

    @capture_overlay_last_layout.setter
    def capture_overlay_last_layout(
        self, value: CaptureOverlayLayout | None,
    ) -> None:
        self.capture.last_layout = value

    @property
    def info_overlay_root(self) -> Any | None:
        return self.info.root

    @info_overlay_root.setter
    def info_overlay_root(self, value: Any | None) -> None:
        self.info.root = value

    @property
    def info_overlay_canvas(self) -> Any | None:
        return self.info.canvas

    @info_overlay_canvas.setter
    def info_overlay_canvas(self, value: Any | None) -> None:
        self.info.canvas = value

    @property
    def info_text_id(self) -> int | None:
        return self.info.text_id

    @info_text_id.setter
    def info_text_id(self, value: int | None) -> None:
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
    def anchor_overlay_root(self) -> Any | None:
        return self.anchor.root

    @anchor_overlay_root.setter
    def anchor_overlay_root(self, value: Any | None) -> None:
        self.anchor.root = value

    @property
    def anchor_overlay_canvas(self) -> Any | None:
        return self.anchor.canvas

    @anchor_overlay_canvas.setter
    def anchor_overlay_canvas(self, value: Any | None) -> None:
        self.anchor.canvas = value

    @property
    def anchor_rect_id(self) -> int | None:
        return self.anchor.rect_id

    @anchor_rect_id.setter
    def anchor_rect_id(self, value: int | None) -> None:
        self.anchor.rect_id = value

    @property
    def anchor_overlay_visible(self) -> bool:
        return self.anchor.visible

    @anchor_overlay_visible.setter
    def anchor_overlay_visible(self, value: bool) -> None:
        self.anchor.visible = value
