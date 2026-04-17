"""Auto-alignment background service."""

from typing import Callable, Optional, Tuple
from scanning_tool.services.base_service import BaseService
from scanning_tool.core.AnchorRegionTracker import AnchorRegionTracker
from scanning_tool.domain.models import AlignmentInfo, AnchorDetection

SyncCallback = Callable[[], None]


def reset_alignment_info(info: AlignmentInfo) -> None:
    info.matched = False
    info.template = None
    info.score = 0.0
    info.match_left = None
    info.match_top = None
    info.capture_left = None
    info.capture_top = None


class AlignmentService(BaseService):
    """Manages continuous alignment calculations for screen anchor points."""

    def _on_start(self) -> None:
        self.logger.info("Starting auto-alignment service.")

    def _on_stop(self) -> None:
        self.logger.info("Stopping auto-alignment tracking.")

    def align(self,
        anchor_tracker: Optional[AnchorRegionTracker],
        last_alignment_info: AlignmentInfo,
        sync_capture_sliders: SyncCallback,
        update_capture_overlay_region: SyncCallback,
    ) -> bool:
        """Attempt to adjust the capture region based on anchor template matches."""
        from scanning_tool.core.state_manager import config

        last_alignment_info.enabled = config.auto_alignment.enabled

        if not config.auto_alignment.enabled:
            return False

        if anchor_tracker is None:
            self.logger.debug("Anchor tracker not initialised; skipping auto alignment.")
            return False

        anchor_tracker.set_threshold(float(config.anchor_threshold))
        detection = anchor_tracker.locate_anchor(config.anchor_template)

        if not detection:
            reset_alignment_info(last_alignment_info)
            return False

        new_left, new_top = self._calculate_aligned_position(detection, config)
        config.capture_region.left = max(0, new_left)
        config.capture_region.top = max(0, new_top)

        self._apply_alignment(last_alignment_info, detection, config)
        sync_capture_sliders()
        update_capture_overlay_region()

        self.logger.debug(
            "Auto alignment applied using %s (score %.3f) => CAP_REGION left/top updated to (%d, %d)",
            detection.template,
            detection.score,
            config.capture_region.left,
            config.capture_region.top,
        )
        return True

    def _calculate_aligned_position(self, detection: AnchorDetection, config) -> Tuple[int, int]:
        base_left = detection.match_left + (detection.template_width / 2.0) - (config.capture_region.width / 2.0)
        base_top = detection.match_top + (detection.template_height / 2.0) - (config.capture_region.height / 2.0)
        new_left = int(round(base_left + config.anchor_offset.x))
        new_top = int(round(base_top + config.anchor_offset.y))
        return new_left, new_top

    def _apply_alignment(self, info: AlignmentInfo, detection: AnchorDetection, config) -> None:
        info.matched = True
        info.template = detection.template
        info.score = detection.score
        info.match_left = detection.match_left
        info.match_top = detection.match_top
        info.capture_left = config.capture_region.left
        info.capture_top = config.capture_region.top


alignment_service = AlignmentService()
