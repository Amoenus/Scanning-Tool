"""Capture overlay window lifecycle and animation."""

import tkinter as tk
from dataclasses import dataclass
from typing import Optional

from .base import CAPTURE_ANIMATION_INTERVAL_MS, create_overlay_window, safe_tk
from .geometry import compute_capture_overlay_layout
from scanning_tool.state.manager import overlay_state
from scanning_tool.gui.layout import CaptureOverlayLayout


@dataclass(frozen=True)
class _CaptureOverlayLayoutChange:
    size_changed: bool
    pos_changed: bool
    rect_changed: bool


class CaptureOverlay:
    def __init__(self) -> None:
        self.root: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.rect_id: Optional[int] = None
        self.border_canvas: Optional[tk.Canvas] = None
        self.animation_job: Optional[str] = None
        self.last_layout: Optional[CaptureOverlayLayout] = None

    def _compute_layout_change(
        self, layout: CaptureOverlayLayout, force: bool
    ) -> _CaptureOverlayLayoutChange:
        last = self.last_layout
        if last is None:
            return _CaptureOverlayLayoutChange(True, True, True)
        return _CaptureOverlayLayoutChange(
            size_changed=(
                force
                or last.overlay_width != layout.overlay_width
                or last.overlay_height != layout.overlay_height
            ),
            pos_changed=(
                force or last.left != layout.left or last.top != layout.top
            ),
            rect_changed=(
                force
                or last.cap_w != layout.cap_w
                or last.cap_h != layout.cap_h
            ),
        )

    def _apply_overlay_size(self, layout: CaptureOverlayLayout) -> None:
        canvas = self.canvas
        assert canvas is not None
        safe_tk(
            lambda: canvas.config(
                width=layout.overlay_width, height=layout.overlay_height
            )
        )

    def _apply_overlay_rectangle(self, layout: CaptureOverlayLayout) -> None:
        canvas = self.canvas
        rect_id = self.rect_id
        assert canvas is not None and rect_id is not None
        safe_tk(
            lambda: canvas.coords(
                rect_id,
                layout.padding_x // 2,
                layout.padding_y,
                layout.padding_x // 2 + layout.cap_w,
                layout.padding_y + layout.cap_h,
            )
        )

    def _apply_overlay_position(self, layout: CaptureOverlayLayout) -> None:
        root = self.root
        assert root is not None
        safe_tk(
            lambda: root.geometry(
                f"{layout.overlay_width}x{layout.overlay_height}+{layout.left}+{layout.top}"
            )
        )
        safe_tk(lambda: root.lift())

    def _apply_layout(self, *, force: bool = False) -> None:
        layout = compute_capture_overlay_layout()
        layout_change = self._compute_layout_change(layout, force=force)

        if layout_change.size_changed:
            self._apply_overlay_size(layout)

        if layout_change.rect_changed:
            self._apply_overlay_rectangle(layout)

        if layout_change.size_changed or layout_change.pos_changed:
            self._apply_overlay_position(layout)

        self.last_layout = layout

    def _schedule_animation(self) -> None:
        if not self.root:
            self.animation_job = None
            return

        self.animation_job = self.root.after(
            CAPTURE_ANIMATION_INTERVAL_MS, self._animate_overlay
        )

    def _animate_overlay(self) -> None:
        if (
            not self.root
            or not self.canvas
            or not self.rect_id
            or safe_tk(self.root.winfo_exists, False) is False
        ):
            self.animation_job = None
            return

        try:
            self._apply_layout()
        except tk.TclError:
            self.animation_job = None
            return

        safe_tk(self._schedule_animation)

    def show(self) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.stop_animation()
                self.root.destroy()
            except tk.TclError:
                pass
            self.canvas = None
            self.rect_id = None
            self.border_canvas = None

        layout = compute_capture_overlay_layout()
        self.root = create_overlay_window(
            layout.overlay_width, layout.overlay_height, layout.left, layout.top
        )
        self.canvas = tk.Canvas(
            self.root,
            width=layout.overlay_width,
            height=layout.overlay_height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.border_canvas = self.canvas

        self.rect_id = self.canvas.create_rectangle(
            layout.padding_x // 2,
            layout.padding_y,
            layout.padding_x // 2 + layout.cap_w,
            layout.padding_y + layout.cap_h,
            outline="red",
            width=3,
            tags=("border",),
        )

        overlay_state.capture_overlay_root = self.root
        overlay_state.capture_overlay_canvas = self.canvas
        overlay_state.capture_rect_id = self.rect_id
        overlay_state.border_canvas = self.border_canvas

        self.start_animation(force=True)

    def start_animation(self, *, force: bool = False) -> None:
        self._apply_layout(force=force)

        if self.animation_job is None:
            self._schedule_animation()

    def stop_animation(self) -> None:
        if self.animation_job is not None and self.root:
            try:
                self.root.after_cancel(self.animation_job)
            except (tk.TclError, ValueError):
                pass
        self.animation_job = None
        self.last_layout = None

    def update_region(self) -> None:
        self.start_animation(force=True)

    def hide(self) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.stop_animation()
                self.root.destroy()
            except tk.TclError:
                pass

        self.root = None
        self.canvas = None
        self.rect_id = None
        self.border_canvas = None
        self.animation_job = None

        overlay_state.capture_overlay_root = None
        overlay_state.capture_overlay_canvas = None
        overlay_state.capture_rect_id = None
        overlay_state.border_canvas = None


_capture_overlay = CaptureOverlay()


def start_capture_overlay_animation(*, force: bool = False) -> None:
    _capture_overlay.start_animation(force=force)


def stop_capture_overlay_animation() -> None:
    _capture_overlay.stop_animation()


def update_capture_overlay_region() -> None:
    _capture_overlay.update_region()


def show_capture_overlay() -> None:
    _capture_overlay.show()


def hide_capture_overlay() -> None:
    _capture_overlay.hide()
