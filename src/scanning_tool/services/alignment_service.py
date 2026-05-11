"""Auto-alignment background service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.domain.alignment import AlignmentAppliedEvent
from scanning_tool.services.alignment_calculator import AlignmentCalculator
from scanning_tool.services.base_service import BaseService
from scanning_tool.state.signals import (
    alignment_applied_signal,
    alignment_failed,
    alignment_requested,
    alignment_reset,
)

if TYPE_CHECKING:
    from scanning_tool.core.anchor import AnchorRegionTracker
    from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest, AnchorDetection, CaptureRegion


def reset_alignment_info(info: AlignmentInfo) -> None:
    info.reset()


class AlignmentService(BaseService):
    """Manages continuous alignment calculations for screen anchor points."""

    def _on_start(self) -> None:
        self.logger.info("Starting auto-alignment service.")

    def _on_stop(self) -> None:
        self.logger.info("Stopping auto-alignment tracking.")

    def align(
        self,
        anchor_tracker: AnchorRegionTracker | None,
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
    ) -> bool:
        """Attempt to adjust the capture region based on anchor template matches."""
        last_alignment_info.enabled = alignment_request.enabled

        if not alignment_request.enabled:
            return False

        alignment_requested.send(self, alignment_request=alignment_request)

        if anchor_tracker is None:
            self.logger.debug(
                "Anchor tracker not initialised; skipping auto alignment.",
            )
            alignment_failed.send(
                self,
                reason="missing_anchor_tracker",
                alignment_request=alignment_request,
            )
            return False

        anchor_tracker.set_threshold(alignment_request.threshold)
        detection = anchor_tracker.locate_anchor(alignment_request.anchor_template)

        if not detection:
            self._reset_alignment(last_alignment_info)
            alignment_reset.send(self, last_alignment_info=last_alignment_info)
            return False

        self._apply_alignment(
            detection,
            alignment_request,
            last_alignment_info,
        )
        return True

    def _reset_alignment(self, last_alignment_info: AlignmentInfo) -> None:
        reset_alignment_info(last_alignment_info)

    def _apply_alignment(
        self,
        detection: AnchorDetection,
        alignment_request: AlignmentRequest,
        last_alignment_info: AlignmentInfo,
    ) -> None:
        new_left, new_top = AlignmentCalculator.calculate_aligned_position(
            detection,
            alignment_request.capture_region,
            alignment_request.anchor_offset,
        )
        alignment_request.capture_region.left = max(0, new_left)
        alignment_request.capture_region.top = max(0, new_top)

        last_alignment_info.update_from_detection(
            detection,
            alignment_request.capture_region,
        )
        alignment_applied_signal.send(
            self,
            event=AlignmentAppliedEvent(
                detection=detection,
                capture_region=alignment_request.capture_region,
            ),
        )
        self._log_alignment_applied(detection, alignment_request.capture_region)

    def _log_alignment_applied(
        self,
        detection: AnchorDetection,
        capture_region: CaptureRegion,
    ) -> None:
        self.logger.debug(
            "Auto alignment applied using %s (score %.3f) => CAP_REGION left/top updated to (%d, %d)",
            detection.template,
            detection.score,
            capture_region.left,
            capture_region.top,
        )


alignment_service = AlignmentService()
