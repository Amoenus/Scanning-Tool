"""Mobile overlay section — open and share the mobile UI for scanning results."""

from __future__ import annotations

import io
import tkinter as tk
import webbrowser
from tkinter import ttk
from typing import TYPE_CHECKING

import segno
from loguru import logger
from PIL import Image, ImageTk

from scanning_tool.gui.tk.widgets import create_button_row, create_status_label
from scanning_tool.web import get_local_ip as get_local_ip_from_web

if TYPE_CHECKING:
    from scanning_tool.gui.tk.sections.base import SectionContext


def get_local_ip() -> str:
    return get_local_ip_from_web()


class MobileOverlaySection:
    """Provides quick access to the mobile UI overlay."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Mobile UI", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status
        self._help_text = tk.StringVar(
            value="Open the mobile UI in a browser or scan a QR code from your phone.",
        )

        self._build_action_row(frame)
        create_status_label(frame, self._help_text)

        return frame

    def _build_action_row(self, parent: ttk.Widget) -> None:
        create_button_row(
            parent,
            [
                ("Open Mobile UI", self._open_mobile_overlay),
                ("Mobile QR Code", self._show_mobile_qr),
            ],
        )

    def _open_mobile_overlay(self) -> None:
        url = self._build_mobile_overlay_url()

        try:
            webbrowser.open_new_tab(url)
        except Exception as exc:
            self._status.set_status(f"Unable to open browser: {exc}")
            logger.warning("Failed to open mobile overlay URL {}: {}", url, exc)
        else:
            self._status.set_status(f"Opening overlay in browser: {url}")
            logger.info("Opened mobile overlay URL: {}", url)

    def _show_mobile_qr(self) -> None:
        url = self._build_mobile_overlay_url()

        try:
            qr = segno.make(url, error="h")
        except Exception as exc:
            self._status.set_status(f"Unable to generate QR code: {exc}")
            logger.warning("Failed to generate QR code for {}: {}", url, exc)
            return

        with io.BytesIO() as buffer:
            qr.save(buffer, kind="png", scale=8, border=2)
            buffer.seek(0)
            image = Image.open(buffer)
            photo = ImageTk.PhotoImage(image)

        self._display_mobile_qr(photo, url)

    def _display_mobile_qr(self, photo: ImageTk.PhotoImage, url: str) -> None:
        window = tk.Toplevel()
        window.title("Scan to Open Mobile UI")
        window.resizable(False, False)
        window.attributes("-topmost", True)

        image_label = ttk.Label(window, image=photo)
        image_label.image = photo
        image_label.pack(padx=12, pady=(12, 6))

        url_label = ttk.Label(window, text=url, wraplength=380, justify="center")
        url_label.pack(padx=12, pady=(0, 12))

        create_button_row(
            window,
            [
                ("Close", window.destroy),
            ],
        )

        self._status.set_status("Mobile overlay QR code displayed. Scan it with your phone.")
        logger.info("Displayed mobile overlay QR code for {}.", url)

    def _build_mobile_overlay_url(self) -> str:
        if hasattr(self, "_ctx"):
            web_config = self._ctx.config.web_server_config
        else:
            from scanning_tool.state.manager import config

            web_config = config.web_server_config

        display_host = self._resolve_mobile_overlay_display_host(web_config.host)
        return f"http://{display_host}:{web_config.port}"

    def _resolve_mobile_overlay_display_host(self, host: str) -> str:
        if host == "0.0.0.0":
            return get_local_ip()
        return host or "127.0.0.1"
