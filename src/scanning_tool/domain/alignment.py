from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mss.models import Monitor


if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData


    from scanning_tool.domain.common import MssMonitor, Offset2D
@dataclass
class CaptureRegion:
    """Represents a capture region on the screen."""

    left: int
    top: int
    width: int
    height: int

    def to_mss_monitor(self) -> MssMonitor:
        """Return an mss-compatible monitor dict for this region."""
        return {
            "left": int(self.left),
            "top": int(self.top),
            "width": int(self.width),
            "height": int(self.height),
        }

    def to_monitor(self) -> Monitor:
        """Return an mss Monitor object for this region."""
        return {
            "left": int(self.left),
            "top": int(self.top),
            "width": int(self.width),
            "height": int(self.height),
        }

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Return an mss-compatible tuple representation for this region."""
        return (self.left, self.top, self.width, self.height)


@dataclass
class AnchorDetection:
    """Result of an anchor template match on a captured region."""

    match_left: float
    match_top: float
    score: float
    template: str
    template_width: float
    template_height: float


@dataclass
class AlignmentInfo:
    """Represents the current alignment state for anchor/template matching."""

    enabled: bool = True
    matched: bool = False
    template: str | None = None
    score: float = 0.0
    match_left: int | None = None
    match_top: int | None = None
    capture_left: int | None = None
    capture_top: int | None = None

    def reset(self) -> None:
        """Clear the alignment result state for a fresh evaluation."""
        self.matched = False
        self.template = None
        self.score = 0.0
        self.match_left = None
        self.match_top = None
        self.capture_left = None
        self.capture_top = None

    def update_from_detection(
        self, detection: AnchorDetection, capture_region: CaptureRegion,
    ) -> None:
        """Update this alignment state from a successful anchor detection."""
        self.matched = True
        self.template = detection.template
        self.score = detection.score
        self.match_left = int(round(detection.match_left))
        self.match_top = int(round(detection.match_top))
        self.capture_left = capture_region.left
        self.capture_top = capture_region.top


@dataclass(frozen=True)
class AlignmentRequest:
    """Request payload containing the inputs required for an alignment run."""

    enabled: bool
    threshold: float
    anchor_template: CaptureRegion
    anchor_offset: Offset2D
    capture_region: CaptureRegion

    @classmethod
    def from_config(cls, config: ConfigData) -> AlignmentRequest:
        return cls(
            enabled=config.auto_alignment.enabled,
            threshold=float(config.anchor_threshold),
            anchor_template=config.anchor_template,
            anchor_offset=config.anchor_offset,
            capture_region=config.capture_region,
        )
