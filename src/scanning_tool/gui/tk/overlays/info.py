"""Floating info overlay and label management."""
from __future__ import annotations


import time
import tkinter as tk
from tkinter import colorchooser


from ..layout import InfoOverlayGeometry, InfoOverlayLayout
from .base import create_overlay_window, safe_tk
from .capture import _capture_overlay
from .geometry import compute_info_overlay_geometry


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.domain.capture import DepositInfo
    from scanning_tool.config.models import OverlayConfig
class InfoOverlay:
    def __init__(self) -> None:
        self.root: tk.Toplevel | None = None
        self.canvas: tk.Canvas | None = None
        self.text_id: int | None = None
        self.info_overlay_geometry: InfoOverlayGeometry = InfoOverlayGeometry()
        self.overlay_text: str = ""
        self.last_overlay_time: float = 0.0
        self._overlay_config: OverlayConfig | None = None

    def _build_deposit_message(self, info: DepositInfo | None) -> str:
        if not info:
            return ""
        name = info.name or ""
        deposits = info.deposits
        return f"{name} x{deposits}" if deposits is not None else name

    def _update_canvas_text(self) -> None:
        canvas = self.canvas
        text_id = self.text_id
        if (
            canvas is not None
            and text_id is not None
            and self._overlay_config is not None
        ):
            fill_color = self._overlay_config.label_color
            safe_tk(
                lambda: canvas.itemconfig(
                    text_id,
                    text=self.overlay_text,
                    fill=fill_color,
                ),
            )

    def update_label(
        self,
        info: DepositInfo | None,
        overlay_state: OverlayState,
        overlay_config: OverlayConfig,
        *,
        code: str | None = None,
        raw_text: str | None = None,
    ) -> None:
        self._overlay_config = overlay_config
        self.overlay_text = self._build_deposit_message(info)
        self.last_overlay_time = time.time() if self.overlay_text else 0

        overlay_state.overlay_text = self.overlay_text
        overlay_state.last_overlay_time = self.last_overlay_time

        self._update_canvas_text()

    def reposition(
        self,
        overlay_state: OverlayState,
        overlay_config: OverlayConfig,
    ) -> None:
        root = self.root
        canvas = self.canvas
        text_id = self.text_id
        if root is None or canvas is None or text_id is None:
            return
        if safe_tk(root.winfo_exists, False) is False:
            return

        screen_width = safe_tk(root.winfo_screenwidth, 1920) or 1920
        screen_height = safe_tk(root.winfo_screenheight, 1080) or 1080

        geo = compute_info_overlay_geometry(screen_width, screen_height, overlay_config)

        safe_tk(lambda: root.geometry(f"{geo.width}x{geo.height}+{geo.left}+{geo.top}"))
        safe_tk(lambda: canvas.config(width=geo.width, height=geo.height))
        safe_tk(lambda: canvas.coords(text_id, geo.width // 2, geo.height // 2))
        safe_tk(lambda: canvas.itemconfig(text_id, width=geo.width - 60))

        self.info_overlay_geometry.screen_width = screen_width
        self.info_overlay_geometry.screen_height = screen_height
        self.info_overlay_geometry.width = geo.width
        self.info_overlay_geometry.height = geo.height
        overlay_state.info_overlay_geometry = self.info_overlay_geometry

    def start_label_timeout(self, overlay_state: OverlayState) -> None:
        canvas = self.canvas
        text_id = self.text_id
        if canvas is not None and text_id is not None:
            if self.last_overlay_time and (time.time() - self.last_overlay_time > 10):
                safe_tk(lambda: canvas.itemconfig(text_id, text=""))
                self.last_overlay_time = 0
                overlay_state.last_overlay_time = 0

        root = self.root
        if root is not None and safe_tk(root.winfo_exists, False):
            safe_tk(
                lambda: root.after(500, lambda: self.start_label_timeout(overlay_state)),
            )

    def _destroy_existing(self) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.root.destroy()
            except tk.TclError:
                pass
            self.canvas = None
            self.text_id = None

    def _create_overlay_canvas(self, geo: InfoOverlayLayout) -> None:
        self.root = create_overlay_window(geo.width, geo.height, geo.left, geo.top)
        self.canvas = tk.Canvas(
            self.root,
            width=geo.width,
            height=geo.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.text_id = self.canvas.create_text(
            geo.width // 2,
            geo.height // 2,
            text=self.overlay_text,
            fill=self._overlay_config.label_color if self._overlay_config else "white",
            font=("Arial", 18, "bold"),
            width=geo.width - 60,
            justify="center",
        )

    def _save_geometry_state(
        self,
        geo: InfoOverlayLayout,
        screen_width: int,
        screen_height: int,
        overlay_state: OverlayState,
    ) -> None:
        self.info_overlay_geometry.screen_width = screen_width
        self.info_overlay_geometry.screen_height = screen_height
        self.info_overlay_geometry.width = geo.width
        self.info_overlay_geometry.height = geo.height
        overlay_state.info_overlay_root = self.root
        overlay_state.info_overlay_canvas = self.canvas
        overlay_state.info_text_id = self.text_id
        overlay_state.info_overlay_geometry = self.info_overlay_geometry

    def show(
        self,
        screen_width: int,
        screen_height: int,
        overlay_state: OverlayState,
        overlay_config: OverlayConfig,
    ) -> None:
        self._overlay_config = overlay_config
        self._destroy_existing()
        geo = compute_info_overlay_geometry(screen_width, screen_height, overlay_config)
        self._create_overlay_canvas(geo)
        self._save_geometry_state(geo, screen_width, screen_height, overlay_state)
        self.start_label_timeout(overlay_state)

    def hide(self, overlay_state: OverlayState) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.root.destroy()
            except tk.TclError:
                pass

        self.root = None
        self.canvas = None
        self.text_id = None

        overlay_state.info_overlay_root = None
        overlay_state.info_overlay_canvas = None
        overlay_state.info_text_id = None


_info_overlay = InfoOverlay()


def update_overlay_label(
    info: DepositInfo | None,
    overlay_state: OverlayState,
    overlay_config: OverlayConfig,
    *,
    code: str | None = None,
    raw_text: str | None = None,
) -> None:
    _info_overlay.update_label(
        info,
        overlay_state=overlay_state,
        overlay_config=overlay_config,
        code=code,
        raw_text=raw_text,
    )


def reposition_info_overlay(
    overlay_state: OverlayState, overlay_config: OverlayConfig,
) -> None:
    _info_overlay.reposition(overlay_state, overlay_config)


def start_label_timeout(overlay_state: OverlayState) -> None:
    _info_overlay.start_label_timeout(overlay_state)


def choose_label_color(overlay_config: OverlayConfig) -> None:
    color = colorchooser.askcolor(title="Choose Label Color")[1]
    if not color:
        return
    overlay_config.label_color = color
    canvas = _info_overlay.canvas
    text_id = _info_overlay.text_id
    if canvas is not None and text_id is not None:
        safe_tk(
            lambda: canvas.itemconfig(
                text_id,
                fill=overlay_config.label_color,
            ),
        )


def toggle_border(overlay_state: OverlayState) -> None:
    overlay_state.show_border = not overlay_state.show_border
    border_canvas = _capture_overlay.border_canvas
    if border_canvas is not None:
        safe_tk(
            lambda: border_canvas.itemconfig(
                "border", state="normal" if overlay_state.show_border else "hidden",
            ),
        )


def show_info_overlay(
    screen_width: int,
    screen_height: int,
    overlay_state: OverlayState,
    overlay_config: OverlayConfig,
) -> None:
    _info_overlay.show(screen_width, screen_height, overlay_state, overlay_config)


def hide_info_overlay(overlay_state: OverlayState) -> None:
    _info_overlay.hide(overlay_state)
