from scanning_tool.domain.alignment import (
    AlignmentInfo,
    AlignmentRequest,
    AnchorDetection,
    CaptureRegion,
)
from scanning_tool.domain.common import Offset2D
from scanning_tool.services.alignment_service import AlignmentService


class FakeAnchorTracker:
    def __init__(self, detection=None):
        self.threshold = None
        self.detection = detection
        self.located_template = None

    def set_threshold(self, threshold: float) -> None:
        self.threshold = threshold

    def locate_anchor(self, template: CaptureRegion):
        self.located_template = template
        return self.detection


def test_alignment_service_updates_capture_region_and_callbacks():
    detection = AnchorDetection(
        match_left=100.0,
        match_top=120.0,
        score=0.95,
        template="anchor-template",
        template_width=20.0,
        template_height=15.0,
    )
    anchor_tracker = FakeAnchorTracker(detection=detection)
    alignment_info = AlignmentInfo(enabled=True)
    alignment_request = AlignmentRequest(
        enabled=True,
        threshold=0.4,
        anchor_template=CaptureRegion(left=0, top=0, width=50, height=50),
        anchor_offset=Offset2D(x=5, y=-3),
        capture_region=CaptureRegion(left=10, top=20, width=80, height=80),
    )

    sync_called = False
    overlay_called = False

    def on_alignment_applied(sender: object, event: object | None = None) -> None:
        nonlocal sync_called
        nonlocal overlay_called
        sync_called = True
        overlay_called = True

    from scanning_tool.state.signals import alignment_applied_signal

    alignment_applied_signal.connect(on_alignment_applied, weak=False)
    try:
        service = AlignmentService()
        result = service.align(
            anchor_tracker,
            alignment_info,
            alignment_request,
        )
    finally:
        alignment_applied_signal.disconnect(on_alignment_applied)

    assert result is True
    assert anchor_tracker.threshold == 0.4
    assert sync_called is True
    assert overlay_called is True
    assert alignment_info.matched is True
    assert alignment_info.template == "anchor-template"
    assert alignment_info.capture_left == alignment_request.capture_region.left
    assert alignment_info.capture_top == alignment_request.capture_region.top
    assert alignment_request.capture_region.left >= 0
    assert alignment_request.capture_region.top >= 0


def test_alignment_service_skips_when_anchor_tracker_missing():
    alignment_info = AlignmentInfo(enabled=False)
    alignment_request = AlignmentRequest(
        enabled=True,
        threshold=0.4,
        anchor_template=CaptureRegion(left=0, top=0, width=50, height=50),
        anchor_offset=Offset2D(x=0, y=0),
        capture_region=CaptureRegion(left=10, top=20, width=80, height=80),
    )

    service = AlignmentService()
    result = service.align(
        None,
        alignment_info,
        alignment_request,
    )

    assert result is False
    assert alignment_info.enabled is True
