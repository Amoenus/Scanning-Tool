"""Anchor overlay display and region updates."""

import tkinter as tk
from typing import Optional

from .base import ANCHOR_OVERLAY_PAD, create_overlay_window, safe_tk
from .geometry import compute_anchor_overlay_geometry
from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.gui.overlay_state import OverlayState


class AnchorOverlay:
    def __init__(self) -> None:
        self.root: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.rect_id: Optional[int] = None
        self._anchor_template: Optional[CaptureRegion] = None

    def show(self, overlay_state: OverlayState, anchor_template: CaptureRegion) -> None:
        if not overlay_state.anchor_overlay_visible:
            return

        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.root.destroy()
            except tk.TclError:
                pass
            self.canvas = None
            self.rect_id = None

        self._anchor_template = anchor_template
        geometry = compute_anchor_overlay_geometry(anchor_template)
        self.root = create_overlay_window(
            geometry.width, geometry.height, geometry.left, geometry.top
        )
        self.canvas = tk.Canvas(
            self.root,
            width=geometry.width,
            height=geometry.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.rect_id = self.canvas.create_rectangle(
            ANCHOR_OVERLAY_PAD // 2,
            ANCHOR_OVERLAY_PAD // 2,
            ANCHOR_OVERLAY_PAD // 2 + int(anchor_template.width),
            ANCHOR_OVERLAY_PAD // 2 + int(anchor_template.height),
            outline="#00d4ff",
            width=2,
        )

        self.canvas.create_text(
            geometry.width // 2,
            5,
            text="ANCHOR REGION",
            fill="#00d4ff",
            font=("Arial", 12, "bold"),
            anchor="n",
        )

        overlay_state.anchor_overlay_root = self.root
        overlay_state.anchor_overlay_canvas = self.canvas
        overlay_state.anchor_rect_id = self.rect_id

    def update_region(self, overlay_state: OverlayState) -> None:
        if (
            not overlay_state.anchor_overlay_visible
            or not self.root
            or not self.canvas
            or not self.rect_id
        ):
            return

        anchor_template = self._anchor_template
        if anchor_template is None:
            return

        root = self.root
        canvas = self.canvas
        rect_id = self.rect_id
        assert root is not None and canvas is not None and rect_id is not None

        geometry = compute_anchor_overlay_geometry(anchor_template)
        safe_tk(lambda: canvas.config(width=geometry.width, height=geometry.height))
        safe_tk(
            lambda: canvas.coords(
                rect_id,
                ANCHOR_OVERLAY_PAD // 2,
                ANCHOR_OVERLAY_PAD // 2,
                ANCHOR_OVERLAY_PAD // 2 + int(anchor_template.width),
                ANCHOR_OVERLAY_PAD // 2 + int(anchor_template.height),
            )
        )
        safe_tk(
            lambda: root.geometry(
                f"{geometry.width}x{geometry.height}+{geometry.left}+{geometry.top}"
            )
        )
        safe_tk(lambda: root.lift())

    def hide(self, overlay_state: OverlayState) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.root.destroy()
            except tk.TclError:
                pass

        self.root = None
        self.canvas = None
        self.rect_id = None
        self._anchor_template = None

        overlay_state.anchor_overlay_root = None
        overlay_state.anchor_overlay_canvas = None
        overlay_state.anchor_rect_id = None


_anchor_overlay = AnchorOverlay()


def show_anchor_overlay(
    overlay_state: OverlayState, anchor_template: CaptureRegion
) -> None:
    _anchor_overlay.show(overlay_state, anchor_template)


def update_anchor_overlay_region(overlay_state: OverlayState) -> None:
    _anchor_overlay.update_region(overlay_state)


def hide_anchor_overlay(overlay_state: OverlayState) -> None:
    _anchor_overlay.hide(overlay_state)
