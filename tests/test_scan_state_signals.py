from scanning_tool.domain.alignment import AlignmentInfo, CaptureRegion
from scanning_tool.domain.capture import DepositInfo, ScanResult
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.signals import (
    alignment_info_updated,
    continuous_mode_changed,
    scan_result_updated,
)


def test_scan_state_emits_scan_result_updated_signal() -> None:
    scan_state = ScanState()
    captured_results: list[ScanResult | None] = []

    def on_scan_result_updated(sender: object, scan_result=None) -> None:
        captured_results.append(scan_result)

    scan_result_updated.connect(on_scan_result_updated, weak=False)
    try:
        scan_state.last_result = ScanResult(
            label="ORE123",
            region=CaptureRegion(left=0, top=0, width=1, height=1),
            info=DepositInfo(key="ore123", name="Ore 123", category="rock deposits"),
            code_raw="123",
            raw_text="Detected code 123",
        )
    finally:
        scan_result_updated.disconnect(on_scan_result_updated)

    assert len(captured_results) == 1
    assert captured_results[0] is not None
    assert captured_results[0].label == "ORE123"


def test_scan_state_emits_continuous_mode_changed_signal() -> None:
    scan_state = ScanState()
    mode_changes: list[bool] = []

    def on_continuous_mode_changed(sender: object, continuous_mode: bool) -> None:
        mode_changes.append(continuous_mode)

    continuous_mode_changed.connect(on_continuous_mode_changed, weak=False)
    try:
        scan_state.set_continuous_mode(True)
    finally:
        continuous_mode_changed.disconnect(on_continuous_mode_changed)

    assert mode_changes == [True]


def test_scan_state_emits_alignment_info_updated_signal() -> None:
    scan_state = ScanState()
    alignment_updates: list[AlignmentInfo] = []

    def on_alignment_info_updated(sender: object, alignment_info: AlignmentInfo) -> None:
        alignment_updates.append(alignment_info)

    alignment_info_updated.connect(on_alignment_info_updated, weak=False)
    try:
        scan_state.notify_alignment_info_listeners()
    finally:
        alignment_info_updated.disconnect(on_alignment_info_updated)

    assert len(alignment_updates) == 1
    assert alignment_updates[0] is scan_state.last_alignment_info
