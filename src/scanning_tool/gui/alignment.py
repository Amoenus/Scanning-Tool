"""Periodic anchor-alignment polling for the GUI."""

import tkinter as tk
from typing import Optional

from scanning_tool.services.alignment_service import (
    alignment_service,
    reset_alignment_info,
)
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.models import AlignmentRequest
from scanning_tool.gui.overlays import (
    update_capture_overlay_region,
    sync_capture_sliders,
)
from scanning_tool.gui.overlays.base import safe_tk
from scanning_tool.gui.status import StatusBar
from scanning_tool.state.scan_state import ScanState


class AlignmentPoller:
    """Runs ``alignment_service.align`` on a Tk ``after`` cadence."""

    def __init__(
        self,
        root: tk.Tk,
        status: StatusBar,
        config: ConfigData,
        scan_state: ScanState,
    ) -> None:
        self.root = root
        self.status = status
        self._config = config
        self._scan_state = scan_state

    def start(self) -> None:
        self._tick()

    def _tick(self) -> None:
        message = self._poll()

        if message:
            self.status.push_alignment_message(message)

        safe_tk(
            lambda: self.root.after(
                max(100, int(self._config.alignment_poll_interval_ms)),
                self._tick,
            )
        )

    def _poll(self) -> Optional[str]:
        if not self._config.auto_alignment.enabled:
            reset_alignment_info(self._scan_state.last_alignment_info)
            return "Head sway compensation disabled."

        if not self._has_anchor_templates():
            reset_alignment_info(self._scan_state.last_alignment_info)
            return "Add anchor templates to enable head sway compensation."

        match_found = self._run_alignment()
        return self._build_alignment_status_message(match_found)

    def _has_anchor_templates(self) -> bool:
        tracker = self._scan_state.anchor_tracker
        return tracker is not None and bool(getattr(tracker, "templates", None))

    def _run_alignment(self) -> bool:
        return alignment_service.align(
            self._scan_state.anchor_tracker,
            self._scan_state.last_alignment_info,
            AlignmentRequest.from_config(self._config),
            sync_capture_sliders,
            update_capture_overlay_region,
        )

    def _build_alignment_status_message(self, match_found: bool) -> Optional[str]:
        info = self._scan_state.last_alignment_info
        if info.matched:
            capture_msg = f"Auto alignment adjusted CAP_REGION: {self._config.capture_region}"
            if self.status.status_var.get() != capture_msg:
                self.status.set_status(capture_msg)
            return f"Anchor locked using {info.template} (score {info.score:.2f})."
        if not match_found:
            return "Anchor match not found. Adjust search region or add templates."
        return None
