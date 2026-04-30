"""Tkinter-backed GUI provider package."""

from scanning_tool.state.actions.scan import ScanAction
from scanning_tool.state.manifest import ConcernManifest
from scanning_tool.state.signals.scan import continuous_mode_changed, scan_completed, scan_failed, scan_started

from .provider import TkGuiProvider

MANIFEST = ConcernManifest(
    claimed_concerns=frozenset({"scan_result"}),
    published_actions=frozenset({ScanAction.SINGLE_SCAN, ScanAction.TOGGLE_CONTINUOUS_CAPTURE}),
    subscribed_signals=frozenset({scan_completed, scan_failed, scan_started, continuous_mode_changed}),
)

__all__ = ["MANIFEST", "TkGuiProvider"]
