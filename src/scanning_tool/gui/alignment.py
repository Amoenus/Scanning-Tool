"""Periodic anchor-alignment polling for the GUI."""

import tkinter as tk
from typing import Optional

from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.gui.overlays import update_capture_overlay_region, sync_capture_sliders
from scanning_tool.gui.overlays.base import safe_tk
from scanning_tool.gui.status import StatusBar
from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config


_IDLE_ALIGNMENT_INFO = {
    "matched": False,
    "template": None,
    "score": 0.0,
    "match_left": None,
    "match_top": None,
    "capture_left": None,
    "capture_top": None,
}


class AlignmentPoller:
    """Runs ``perform_auto_alignment`` on a Tk ``after`` cadence."""

    def __init__(self, root: tk.Tk, status: StatusBar) -> None:
        self.root = root
        self.status = status

    def start(self) -> None:
        self._tick()

    def _tick(self) -> None:
        message = self._poll()

        if message:
            self.status.push_alignment_message(message)

        safe_tk(lambda: self.root.after(
            max(100, int(config.alignment_poll_interval_ms)),
            self._tick,
        ))

    def _poll(self) -> Optional[str]:
        if not config.auto_alignment.enabled:
            info = scan_state.last_alignment_info
            info.matched = False
            info.template = None
            info.score = 0.0
            info.match_left = None
            info.match_top = None
            info.capture_left = None
            info.capture_top = None
            return "Head sway compensation disabled."

        tracker = scan_state.anchor_tracker
        if tracker is None or not getattr(tracker, "templates", None):
            info = scan_state.last_alignment_info
            info.matched = False
            info.template = None
            info.score = 0.0
            info.match_left = None
            info.match_top = None
            info.capture_left = None
            info.capture_top = None
            return "Add anchor templates to enable head sway compensation."

        match_found = alignment_service.align(
            scan_state.anchor_tracker,
            config.auto_alignment,
            config.capture_region,
            scan_state.last_alignment_info,
            sync_capture_sliders,
            update_capture_overlay_region,
        )
        info = scan_state.last_alignment_info
        if info.matched:
            capture_msg = f"Auto alignment adjusted CAP_REGION: {config.capture_region}"
            if self.status.status_var.get() != capture_msg:
                self.status.set_status(capture_msg)
            return f"Anchor locked using {info.template} (score {info.score:.2f})."
        if not match_found:
            return "Anchor match not found. Adjust search region or add templates."
        return None
