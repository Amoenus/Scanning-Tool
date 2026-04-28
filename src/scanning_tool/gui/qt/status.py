from __future__ import annotations

import time

from PyQt6.QtCore import QTimer

from scanning_tool.state.signals import status_updated


class StatusBar:
    """Minimal Qt-compatible status bar used by Qt section logic."""

    def __init__(self) -> None:
        self.status_text = "Ready."
        self.anchor_status_text = "Head sway compensation ready."
        self._last_alignment_message: str | None = None
        self._anchor_hold_until = 0.0

    def set_status(self, message: str) -> None:
        self.status_text = message

    def set_status_async(self, sender: object, message: str) -> None:
        QTimer.singleShot(0, lambda: self.set_status(message))

    def set_anchor(self, message: str, hold: float = 1.5) -> None:
        self.anchor_status_text = message
        self._anchor_hold_until = time.time() + hold
        self._last_alignment_message = None

    def anchor_hold_active(self) -> bool:
        return time.time() < self._anchor_hold_until

    def push_alignment_message(self, message: str) -> None:
        if self.anchor_hold_active():
            return
        if message == self._last_alignment_message:
            return
        self.anchor_status_text = message
        self._last_alignment_message = message

    def install_as_scanning_callback(self, service_state: object) -> None:
        status_updated.connect(self.set_status_async, weak=False)
