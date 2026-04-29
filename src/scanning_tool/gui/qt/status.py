from __future__ import annotations

import time

from PyQt6.QtCore import QTimer

from scanning_tool.state.signals import status_updated


class StatusBar:
    """Minimal Qt-compatible status bar used by Qt section logic."""

    def __init__(self) -> None:
        """Initialize the StatusBar with default status messages and timing state."""
        self.status_text = "Ready."
        self.anchor_status_text = "Head sway compensation ready."
        self._last_alignment_message: str | None = None
        self._anchor_hold_until = 0.0

    def set_status(self, message: str) -> None:
        """Set the main status bar message.

        Parameters
        ----------
        message : str
            The message to display in the status bar.

        """
        self.status_text = message

    def set_status_async(self, sender: object, message: str) -> None:
        """Queue an asynchronous update to the status text.

        Parameters
        ----------
        sender : object
            The source of the status update signal.
        message : str
            The message to display in the status bar.

        """
        QTimer.singleShot(0, lambda: self.set_status(message))

    def set_anchor(self, message: str, hold: float = 1.5) -> None:
        """Set the anchor status message and keep it visible for a short duration.

        Parameters
        ----------
        message : str
            The anchor message to display.
        hold : float, optional
            How long, in seconds, to retain the anchor message.

        """
        self.anchor_status_text = message
        self._anchor_hold_until = time.time() + hold
        self._last_alignment_message = None

    def anchor_hold_active(self) -> bool:
        """Return whether the anchor message is still being held.

        Returns
        -------
        bool
            True if the anchor hold period is active, otherwise False.

        """
        return time.time() < self._anchor_hold_until

    def push_alignment_message(self, message: str) -> None:
        """Update the anchor text with an alignment message when not held.

        Parameters
        ----------
        message : str
            The alignment message to display.

        """
        if self.anchor_hold_active():
            return
        if message == self._last_alignment_message:
            return
        self.anchor_status_text = message
        self._last_alignment_message = message

    def install_as_scanning_callback(self, service_state: object) -> None:
        """Install this status bar as a callback for scanning status updates.

        Parameters
        ----------
        service_state : object
            The scanning service state object that may provide callback context.

        """
        status_updated.connect(self.set_status_async, weak=False)
