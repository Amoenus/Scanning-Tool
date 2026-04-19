from __future__ import annotations

from typing import Protocol, Callable, Optional

from PIL.Image import Image

from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest, CaptureRegion
from scanning_tool.domain.capture import DepositInfo

StatusCallback = Callable[[str], None]
SyncCallback = Callable[[], None]


class CaptureProvider(Protocol):
    """Provides a screen capture image for a given capture region."""

    def capture(self, region: CaptureRegion) -> Image:
        ...


class OCRProvider(Protocol):
    """Extract text from an image."""

    def extract_text(self, pil_img: Image) -> str:
        ...


class DepositLookupProvider(Protocol):
    """Lookup deposit metadata from an OCR code."""

    def lookup(self, code: Optional[str]) -> Optional[DepositInfo]:
        ...


class AlignmentAdapter(Protocol):
    """Aligns a capture region using the configured anchor tracker."""

    def align(
        self,
        anchor_tracker: AnchorRegionTracker | None,
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
        sync_capture_sliders: SyncCallback,
        update_capture_overlay_region: SyncCallback,
    ) -> bool:
        ...
