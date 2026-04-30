"""Mobile overlay section for the Qt scanning tool GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import mobile_qr_ready
from scanning_tool.web import get_local_ip as get_local_ip_from_web

from .base import SectionContext

if TYPE_CHECKING:
    from scanning_tool.gui.qt.status import StatusBar


def _get_local_ip() -> str:
    return get_local_ip_from_web()


class MobileOverlaySection:
    """Provides quick access to the mobile UI overlay."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget:
        self._ctx = ctx
        self._status: StatusBar = ctx.status

        group = QGroupBox("Mobile UI", parent)
        layout = QVBoxLayout(group)

        button_layout = QHBoxLayout()
        open_button = QPushButton("Open Mobile UI", group)
        qr_button = QPushButton("Mobile QR Code", group)
        open_button.clicked.connect(self._open_mobile_overlay)
        qr_button.clicked.connect(self._show_mobile_qr)
        button_layout.addWidget(open_button)
        button_layout.addWidget(qr_button)
        layout.addLayout(button_layout)

        self._help_label = QLabel(
            "Open the mobile UI in a browser or scan a QR code from your phone.",
            group,
        )
        self._help_label.setWordWrap(True)
        layout.addWidget(self._help_label)

        mobile_qr_ready.connect(self._on_mobile_qr_ready, weak=False)
        return group

    def _build_mobile_overlay_url(self) -> str:
        web_config = self._ctx.config.web_server_config
        display_host = self._resolve_mobile_overlay_display_host(web_config.host)
        return f"http://{display_host}:{web_config.port}"

    def _resolve_mobile_overlay_display_host(self, host: str) -> str:
        if host == "0.0.0.0":
            return _get_local_ip()
        return host or "127.0.0.1"

    def _open_mobile_overlay(self) -> None:
        url = self._build_mobile_overlay_url()
        publish_ui_action(ConfigAction.OPEN_MOBILE_UI, {"url": url})

    def _show_mobile_qr(self) -> None:
        url = self._build_mobile_overlay_url()
        publish_ui_action(ConfigAction.SHOW_MOBILE_QR, {"url": url})

    def _on_mobile_qr_ready(self, sender: object, url: str, png_bytes: bytes) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(png_bytes)

        dialog = QDialog(self._ctx.root)
        dialog.setWindowTitle("Scan to Open Mobile UI")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        label = QLabel(dialog)
        label.setPixmap(pixmap)
        layout.addWidget(label)
        layout.addWidget(QLabel(url, dialog))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=dialog)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()
        self._status.set_status("Mobile overlay QR code displayed. Scan it with your phone.")
