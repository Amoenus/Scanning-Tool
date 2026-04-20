from __future__ import annotations

from typing import Optional

from scanning_tool.config.service import ConfigData
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.state.scan_state import ScanState
from scanning_tool.domain.capture import ScanResult


def test_scan_state_scan_result_listener_is_called() -> None:
    scan_state = ScanState()
    received: list[Optional[ScanResult]] = []

    scan_state.add_scan_result_listener(lambda result: received.append(result))

    expected = ScanResult(
        label="TEST",
        region=ConfigData().capture_region,
    )
    scan_state.last_result = expected

    assert received == [expected]


def test_scan_state_alignment_info_listener_is_called() -> None:
    scan_state = ScanState()
    received: list[bool] = []

    scan_state.add_alignment_info_listener(
        lambda info: received.append(info.enabled)
    )

    scan_state.last_alignment_info.enabled = True
    scan_state.notify_alignment_info_listeners()

    assert received == [True]


def test_overlay_state_capture_root_listener_is_called() -> None:
    overlay_state = OverlayState()
    received: list[Optional[object]] = []

    overlay_state.add_capture_overlay_root_listener(lambda root: received.append(root))

    root_object = object()
    overlay_state.capture_overlay_root = root_object
    overlay_state.capture_overlay_root = None

    assert received == [root_object, None]
