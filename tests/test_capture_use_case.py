from PIL import Image

from scanning_tool.application.capture import CaptureUseCase
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.capture import DepositInfo
from scanning_tool.services.capture_provider import ScreenCaptureUnavailableError
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.signals import (
    scan_completed,
    scan_failed,
    scan_started,
)


class FakeCaptureProvider:
    def capture(self, region):
        return Image.new("RGB", (region.width, region.height), "black")


class FakeOCRProvider:
    def extract_text(self, pil_img):
        return "12345"


class FakeDepositLookupProvider:
    def lookup(self, code):
        return DepositInfo(name="Test Ore", category="rock deposits")


class FakeAlignmentAdapter:
    def align(
        self,
        anchor_tracker,
        last_alignment_info,
        alignment_request,
    ):
        return False


def test_capture_use_case_populates_scan_state_and_returns_deposit_info():
    config = ConfigData()
    scan_state = ScanState()
    use_case = CaptureUseCase(
        config=config,
        scan_state=scan_state,
        capture_provider=FakeCaptureProvider(),
        ocr_provider=FakeOCRProvider(),
        deposit_lookup=FakeDepositLookupProvider(),
        alignment_adapter=FakeAlignmentAdapter(),
    )

    statuses: list[str] = []

    use_case.capture_once(status_callback=lambda message: statuses.append(message))

    assert scan_state.last_result is not None
    assert scan_state.last_result.label == "12345"
    assert scan_state.last_result.info is not None
    assert scan_state.last_result.info.name == "Test Ore"
    assert statuses and "Scan complete." in statuses[-1]


def test_capture_use_case_handles_locked_screen_gracefully():
    class LockedScreenCaptureProvider:
        def capture(self, region):
            raise ScreenCaptureUnavailableError(
                "Screen capture unavailable: display may be locked.",
            )

    config = ConfigData()
    scan_state = ScanState()
    use_case = CaptureUseCase(
        config=config,
        scan_state=scan_state,
        capture_provider=LockedScreenCaptureProvider(),
        ocr_provider=FakeOCRProvider(),
        deposit_lookup=FakeDepositLookupProvider(),
        alignment_adapter=FakeAlignmentAdapter(),
    )

    statuses: list[str] = []
    use_case.capture_once(status_callback=lambda message: statuses.append(message))

    assert scan_state.last_result is None
    assert any(
        "Screen capture unavailable" in status for status in statuses
    )


def test_capture_use_case_emits_capture_signals_for_success():
    config = ConfigData()
    scan_state = ScanState()
    use_case = CaptureUseCase(
        config=config,
        scan_state=scan_state,
        capture_provider=FakeCaptureProvider(),
        ocr_provider=FakeOCRProvider(),
        deposit_lookup=FakeDepositLookupProvider(),
        alignment_adapter=FakeAlignmentAdapter(),
    )

    started = False
    completed_result = None

    def on_started(sender: object) -> None:
        nonlocal started
        started = True

    def on_completed(sender: object, scan_result=None) -> None:
        nonlocal completed_result
        completed_result = scan_result

    scan_started.connect(on_started, weak=False)
    scan_completed.connect(on_completed, weak=False)
    try:
        use_case.capture_once()
    finally:
        scan_started.disconnect(on_started)
        scan_completed.disconnect(on_completed)

    assert started is True
    assert completed_result is not None
    assert completed_result.label == "12345"
    assert completed_result.info.name == "Test Ore"


def test_capture_use_case_emits_capture_failed_signal_for_lock():
    class LockedScreenCaptureProvider:
        def capture(self, region):
            raise ScreenCaptureUnavailableError(
                "Screen capture unavailable: display may be locked.",
            )

    config = ConfigData()
    scan_state = ScanState()
    use_case = CaptureUseCase(
        config=config,
        scan_state=scan_state,
        capture_provider=LockedScreenCaptureProvider(),
        ocr_provider=FakeOCRProvider(),
        deposit_lookup=FakeDepositLookupProvider(),
        alignment_adapter=FakeAlignmentAdapter(),
    )

    failed_args = None

    def on_failed(sender: object, error=None):
        nonlocal failed_args
        failed_args = error

    scan_failed.connect(on_failed, weak=False)
    try:
        use_case.capture_once()
    finally:
        scan_failed.disconnect(on_failed)

    assert isinstance(failed_args, ScreenCaptureUnavailableError)
