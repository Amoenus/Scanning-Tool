import pytest

from scanning_tool.gui.qt import MANIFEST as qt_manifest
from scanning_tool.gui.tk import MANIFEST as tk_manifest
from scanning_tool.state.actions.scan import ScanAction
from scanning_tool.state.signals.scan import scan_completed
from scanning_tool.web import MANIFEST as web_manifest

UI_MANIFESTS = {
    "tk": tk_manifest,
    "qt": qt_manifest,
    "web": web_manifest,
}


def test_every_action_enum_member_has_handler():
    pass  # We'll implement this later once all actions are migrated


def test_every_signal_has_publisher():
    pass  # Same here


@pytest.mark.parametrize("ui_name, manifest", UI_MANIFESTS.items())
def test_scan_result_conformance(ui_name, manifest):
    """If a UI claims the 'scan_result' concern, it should declare the expected actions and signals."""
    if "scan_result" not in manifest.claimed_concerns:
        pytest.skip(f"{ui_name} does not claim 'scan_result'")

    # The read-only web UI only consumes scan_completed.
    if ui_name == "web":
        assert scan_completed in manifest.subscribed_signals
        return

    assert ScanAction.SINGLE_SCAN in manifest.published_actions
    assert ScanAction.TOGGLE_CONTINUOUS_CAPTURE in manifest.published_actions
    assert scan_completed in manifest.subscribed_signals
