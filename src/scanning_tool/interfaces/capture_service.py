from __future__ import annotations

from typing import Protocol

from scanning_tool.interfaces.capture import StatusCallback


class CaptureController(Protocol):
    """Control interface for capture operations exposed to the UI."""

    def capture_once(
        self, status_callback: StatusCallback | None = None,
    ) -> None: ...

    def toggle_continuous(self) -> None: ...
