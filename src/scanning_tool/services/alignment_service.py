"""Auto-alignment background service."""

from typing import Callable, Optional, Tuple
from scanning_tool.services.base_service import BaseService
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest, AnchorDetection

SyncCallback = Callable[[], None]


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
        anchor_tracker: Optional[AnchorRegionTracker],
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
        sync_capture_sliders: SyncCallback,
        update_capture_overlay_region: SyncCallback,
    ) -> bool:
        """Attempt to adjust the capture region based on anchor template matches."""
        last_alignment_info.enabled = alignment_request.enabled

        if not alignment_request.enabled:
            return False

        if anchor_tracker is None:
            self.logger.debug(
                "Anchor tracker not initialised; skipping auto alignment."
            )
            return False

        anchor_tracker.set_threshold(alignment_request.threshold)
        detection = anchor_tracker.locate_anchor(alignment_request.anchor_template)

        if not detection:
            reset_alignment_info(last_alignment_info)
            return False

        new_left, new_top = self._calculate_aligned_position(
            detection, alignment_request
        )
        alignment_request.capture_region.left = max(0, new_left)
        alignment_request.capture_region.top = max(0, new_top)

        last_alignment_info.update_from_detection(
            detection, alignment_request.capture_region
        )
        sync_capture_sliders()
        update_capture_overlay_region()

        self.logger.debug(
            "Auto alignment applied using %s (score %.3f) => CAP_REGION left/top updated to (%d, %d)",
            detection.template,
            detection.score,
            alignment_request.capture_region.left,
            alignment_request.capture_region.top,
        )
        return True

    def _calculate_aligned_position(
        self, detection: AnchorDetection, alignment_request: AlignmentRequest
    ) -> Tuple[int, int]:
        base_left = (
            detection.match_left
            + (detection.template_width / 2.0)
            - (alignment_request.capture_region.width / 2.0)
        )
        base_top = (
            detection.match_top
            + (detection.template_height / 2.0)
            - (alignment_request.capture_region.height / 2.0)
        )
        new_left = int(round(base_left + alignment_request.anchor_offset.x))
        new_top = int(round(base_top + alignment_request.anchor_offset.y))
        return new_left, new_top


alignment_service = AlignmentService()
