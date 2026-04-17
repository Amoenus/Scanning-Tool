"""Floating info overlay and label management."""

import time
import tkinter as tk
from tkinter import colorchooser
from typing import Optional

from .base import create_overlay_window, safe_tk
from .capture import _capture_overlay
from .geometry import compute_info_overlay_geometry
from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config
from scanning_tool.domain.models import DepositInfo, InfoOverlayGeometry


class InfoOverlay:
    def __init__(self) -> None:
        self.root: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.text_id: Optional[int] = None
        self.info_overlay_geometry: InfoOverlayGeometry = InfoOverlayGeometry()
        self.overlay_text: str = ""
        self.last_overlay_time: float = 0.0

    def _build_deposit_message(self, info: Optional[DepositInfo]) -> str:
        if not info:
            return ""
        name = info.name or ""
        deposits = info.deposits
        return f"{name} x{deposits}" if deposits is not None else name

    def _update_canvas_text(self) -> None:
        if self.canvas and self.text_id:
            safe_tk(lambda: self.canvas.itemconfig(
                self.text_id,
                text=self.overlay_text,
                fill=config.overlay_config.label_color,
            ))

    def update_label(self, info: Optional[DepositInfo], *, code: Optional[str] = None, raw_text: Optional[str] = None) -> None:
        self.overlay_text = self._build_deposit_message(info)
        self.last_overlay_time = time.time() if self.overlay_text else 0

        overlay_state.overlay_text = self.overlay_text
        overlay_state.last_overlay_time = self.last_overlay_time

        self._update_canvas_text()

    def reposition(self) -> None:
        if not self.root or not self.canvas or not self.text_id:
            return
        if safe_tk(self.root.winfo_exists, False) is False:
            return

        screen_width = safe_tk(self.root.winfo_screenwidth, 1920) or 1920
        screen_height = safe_tk(self.root.winfo_screenheight, 1080) or 1080

        geo = compute_info_overlay_geometry(screen_width, screen_height)

        safe_tk(lambda: self.root.geometry(f"{geo.width}x{geo.height}+{geo.left}+{geo.top}"))
        safe_tk(lambda: self.canvas.config(width=geo.width, height=geo.height))
        safe_tk(lambda: self.canvas.coords(self.text_id, geo.width // 2, geo.height // 2))
        safe_tk(lambda: self.canvas.itemconfig(self.text_id, width=geo.width - 60))

        self.info_overlay_geometry.screen_width = screen_width
        self.info_overlay_geometry.screen_height = screen_height
        self.info_overlay_geometry.width = geo.width
        self.info_overlay_geometry.height = geo.height
        overlay_state.info_overlay_geometry = self.info_overlay_geometry

    def start_label_timeout(self) -> None:
        if self.canvas and self.text_id:
            if self.last_overlay_time and (time.time() - self.last_overlay_time > 10):
                safe_tk(lambda: self.canvas.itemconfig(self.text_id, text=""))
                self.last_overlay_time = 0
                overlay_state.last_overlay_time = 0

        if self.root and safe_tk(self.root.winfo_exists, False):
            safe_tk(lambda: self.root.after(500, self.start_label_timeout))

    def _destroy_existing(self) -> None:
        if self.root and safe_tk(self.root.winfo_exists, False):
            try:
                self.root.destroy()
            except tk.TclError:
                pass
            self.canvas = None
            self.text_id = None

    def _create_overlay_canvas(self, geo: InfoOverlayGeometry) -> None:
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
            fill=config.overlay_config.label_color,
            font=("Arial", 18, "bold"),
            width=geo.width - 60,
            justify="center",
        )

    def _save_geometry_state(self, geo: InfoOverlayGeometry, screen_width: int, screen_height: int) -> None:
        self.info_overlay_geometry.screen_width = screen_width
        self.info_overlay_geometry.screen_height = screen_height
        self.info_overlay_geometry.width = geo.width
        self.info_overlay_geometry.height = geo.height
        overlay_state.info_overlay_root = self.root
        overlay_state.info_overlay_canvas = self.canvas
        overlay_state.info_text_id = self.text_id
        overlay_state.info_overlay_geometry = self.info_overlay_geometry

    def show(self, screen_width: int, screen_height: int) -> None:
        self._destroy_existing()
        geo = compute_info_overlay_geometry(screen_width, screen_height)
        self._create_overlay_canvas(geo)
        self._save_geometry_state(geo, screen_width, screen_height)
        self.start_label_timeout()

    def hide(self) -> None:
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


def update_overlay_label(info: Optional[DepositInfo], *, code: Optional[str] = None, raw_text: Optional[str] = None) -> None:
    _info_overlay.update_label(info, code=code, raw_text=raw_text)


def reposition_info_overlay() -> None:
    _info_overlay.reposition()


def start_label_timeout(window: Optional[tk.Toplevel]) -> None:
    _info_overlay.start_label_timeout()


def choose_label_color() -> None:
    overlay_settings = config.overlay_config
    color = colorchooser.askcolor(title="Choose Label Color")[1]
    if not color:
        return
    overlay_settings.label_color = color
    if _info_overlay.canvas and _info_overlay.text_id:
        safe_tk(lambda: _info_overlay.canvas.itemconfig(
            _info_overlay.text_id,
            fill=overlay_settings.label_color,
        ))


def toggle_border() -> None:
    overlay_state = overlay_state
    overlay_state.show_border = not overlay_state.show_border
    if _capture_overlay.border_canvas:
        safe_tk(lambda: _capture_overlay.border_canvas.itemconfig(
            "border", state="normal" if overlay_state.show_border else "hidden"
        ))


def show_info_overlay(screen_width: int, screen_height: int) -> None:
    _info_overlay.show(screen_width, screen_height)


def hide_info_overlay() -> None:
    _info_overlay.hide()
