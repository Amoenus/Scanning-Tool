from PIL import Image

from scanning_tool.application.capture import CaptureUseCase
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.capture import DepositInfo
from scanning_tool.services.capture_provider import ScreenCaptureUnavailableError
from scanning_tool.state.scan_state import ScanState


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
