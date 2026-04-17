from .anchor_matcher import AnchorMatcher
from .anchor_template_loader import AnchorTemplate, AnchorTemplateLoader
from scanning_tool.domain.alignment import AnchorDetection, CaptureRegion
from scanning_tool.domain.common import MssMonitor


import cv2
import mss
import numpy as np
from loguru import logger
from mss.models import Monitor


from typing import List, Optional


class AnchorRegionTracker:
    """Manage template loading and anchor matching for auto alignment."""

    def __init__(self, template_dir: str, threshold: float = 0.82) -> None:
        self.template_loader = AnchorTemplateLoader(template_dir)
        self.matcher = AnchorMatcher()
        self.threshold = threshold

    def set_threshold(self, threshold: float) -> None:
        self.threshold = threshold

    def set_directory(self, template_dir: str) -> int:
        return self.template_loader.set_directory(template_dir)

    def load_templates(self) -> int:
        return self.template_loader.load_templates()

    @property
    def templates(self) -> List[AnchorTemplate]:
        return self.template_loader.templates

    @property
    def last_loaded_count(self) -> int:
        return self.template_loader.last_loaded_count

    def _has_templates(self) -> bool:
        return bool(self.template_loader.templates)

    def locate_anchor(self, region: "CaptureRegion") -> Optional[AnchorDetection]:
        """Locate the best matching anchor template within *region*."""
        if not self._has_templates():
            return None

        mss_monitor = region.to_mss_monitor()
        monitor = self._to_library_monitor(mss_monitor)
        anchor_gray = self._grab_anchor_screenshot(monitor)
        if anchor_gray is None:
            return None

        best_score, best_loc, best_template = self.matcher.find_best_match(
            anchor_gray, self.template_loader.templates
        )
        if best_loc is None or best_template is None:
            return None

        if best_score < self.threshold:
            logger.debug(
                f"Anchor match below threshold ({best_score:.3f} < {self.threshold:.3f}) using template {best_template.name}"
            )
            return None

        return self.matcher.build_detection(
            monitor, best_loc, best_template, best_score
        )

    def _grab_anchor_screenshot(self, monitor: Monitor) -> Optional[np.ndarray]:
        with mss.mss() as sct:
            try:
                screenshot = sct.grab(monitor)
            except Exception as exc:
                logger.error(f"Anchor capture failed: {exc}")
                return None

        anchor_image = np.array(screenshot)
        if anchor_image.ndim == 3 and anchor_image.shape[2] == 4:
            return cv2.cvtColor(anchor_image, cv2.COLOR_BGRA2GRAY)
        return cv2.cvtColor(anchor_image, cv2.COLOR_BGR2GRAY)

    def _to_library_monitor(self, monitor: MssMonitor) -> Monitor:
        return {
            "left": monitor["left"],
            "top": monitor["top"],
            "width": monitor["width"],
            "height": monitor["height"],
        }
