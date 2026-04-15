"""Auto-alignment background service."""

from typing import Callable, Optional
from scanning_tool.services.base_service import BaseService
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.runtime.scan_state import AlignmentInfo

SyncCallback = Callable[[], None]

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
            info = last_alignment_info
            info.matched = False
            info.template = None
            info.score = 0.0
            info.match_left = None
            info.match_top = None
            info.capture_left = None
            info.capture_top = None
            return False
    
        base_left = detection.match_left + (detection.template_width / 2.0) - (config.capture_region.width / 2.0)
        base_top = detection.match_top + (detection.template_height / 2.0) - (config.capture_region.height / 2.0)

        new_left = int(round(base_left + config.anchor_offset.get("x", 0)))
        new_top = int(round(base_top + config.anchor_offset.get("y", 0)))

        config.capture_region.left = max(0, new_left)
        config.capture_region.top = max(0, new_top)

        info = last_alignment_info
        info.matched = True
        info.template = detection.template
        info.score = detection.score
        info.match_left = detection.match_left
        info.match_top = detection.match_top
        info.capture_left = config.capture_region.left
        info.capture_top = config.capture_region.top

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


alignment_service = AlignmentService()
