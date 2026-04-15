"""Auto-alignment background service."""

from typing import Callable, Dict, Optional
from scanning_tool.services.base_service import BaseService
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.config.settings import AnchorSettings, CaptureSettings
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
        anchor_settings: AnchorSettings,
        capture_settings: CaptureSettings,
        last_alignment_info: AlignmentInfo,
        sync_capture_sliders: SyncCallback,
        update_capture_overlay_region: SyncCallback,
    ) -> bool:
        """Attempt to adjust the capture region based on anchor template matches."""
        last_alignment_info.enabled = anchor_settings.auto_align_enabled
    
        if not anchor_settings.auto_align_enabled:
            return False
    
        if anchor_tracker is None:
            self.logger.debug("Anchor tracker not initialised; skipping auto alignment.")
            return False
    
        anchor_tracker.set_threshold(float(anchor_settings.anchor_threshold))
        detection = anchor_tracker.locate_anchor(anchor_settings.anchor_region)
    
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
    
        template_w = detection.get("template_width", float(capture_settings.cap_region["width"]))
        template_h = detection.get("template_height", float(capture_settings.cap_region["height"]))
        base_left = detection["match_left"] + (template_w / 2.0) - (capture_settings.cap_region["width"] / 2.0)
        base_top = detection["match_top"] + (template_h / 2.0) - (capture_settings.cap_region["height"] / 2.0)
    
        new_left = int(round(base_left + anchor_settings.anchor_offset.get("x", 0)))
        new_top = int(round(base_top + anchor_settings.anchor_offset.get("y", 0)))
    
        capture_settings.cap_region["left"] = max(0, new_left)
        capture_settings.cap_region["top"] = max(0, new_top)
    
        info = last_alignment_info
        info.matched = True
        info.template = detection["template"]
        info.score = float(detection["score"])
        info.match_left = detection["match_left"]
        info.match_top = detection["match_top"]
        info.capture_left = capture_settings.cap_region["left"]
        info.capture_top = capture_settings.cap_region["top"]
    
        sync_capture_sliders()
        update_capture_overlay_region()
    
        self.logger.debug(
            "Auto alignment applied using %s (score %.3f) => CAP_REGION left/top updated to (%d, %d)",
            detection["template"],
            detection["score"],
            capture_settings.cap_region["left"],
            capture_settings.cap_region["top"],
        )
        return True

alignment_service = AlignmentService()
