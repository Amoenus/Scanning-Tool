from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol

from PIL.Image import Image

if TYPE_CHECKING:
    from scanning_tool.core.anchor import AnchorRegionTracker


    from scanning_tool.domain.capture import DepositInfo
    from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest, CaptureRegion
StatusCallback = Callable[[str], None]


class CaptureProvider(Protocol):
    """Provides a screen capture image for a given capture region."""

    def capture(self, region: CaptureRegion) -> Image: ...


class OCRProvider(Protocol):
    """Extract text from an image."""

    def extract_text(self, pil_img: Image) -> str: ...


class DepositLookupProvider(Protocol):
    """Lookup deposit metadata from an OCR code."""

    def lookup(self, code: str | None) -> DepositInfo | None: ...


class AlignmentAdapter(Protocol):
    """Aligns a capture region using the configured anchor tracker."""

    def align(
        self,
        anchor_tracker: AnchorRegionTracker | None,
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
    ) -> bool: ...
