from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

from .anchor_matcher import AnchorMatcher
from .anchor_template_loader import AnchorTemplate, AnchorTemplateLoader

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AnchorDetection, CaptureRegion
    from scanning_tool.interfaces.capture import CaptureProvider
class AnchorRegionTracker:
    """Manage template loading and anchor matching for auto alignment."""

    def __init__(
        self,
        template_dir: str,
        capture_provider: CaptureProvider,
        threshold: float = 0.82,
    ) -> None:
        self.template_loader = AnchorTemplateLoader(template_dir)
        self.matcher = AnchorMatcher()
        self.threshold = threshold
        self.capture_provider = capture_provider

    def set_threshold(self, threshold: float) -> None:
        self.threshold = threshold

    def set_directory(self, template_dir: str) -> int:
        return self.template_loader.set_directory(template_dir)

    def load_templates(self) -> int:
        return self.template_loader.load_templates()

    @property
    def templates(self) -> list[AnchorTemplate]:
        return self.template_loader.templates

    @property
    def last_loaded_count(self) -> int:
        return self.template_loader.last_loaded_count

    def _has_templates(self) -> bool:
        return bool(self.template_loader.templates)

    def locate_anchor(self, region: CaptureRegion) -> AnchorDetection | None:
        """Locate the best matching anchor template within *region*."""
        if not self._has_templates():
            return None

        monitor = region.to_monitor()
        anchor_gray = self._grab_anchor_screenshot(region)

        best_score, best_loc, best_template = self.matcher.find_best_match(
            anchor_gray, self.template_loader.templates,
        )
        if best_loc is None or best_template is None:
            return None

        if best_score < self.threshold:
            logger.debug(
                f"Anchor match below threshold ({best_score:.3f} < {self.threshold:.3f}) using template {best_template.name}",
            )
            return None

        return self.matcher.build_detection(
            monitor, best_loc, best_template, best_score,
        )

    def _grab_anchor_screenshot(self, region: CaptureRegion) -> np.ndarray:
        screenshot = self.capture_provider.capture(region)
        return np.array(screenshot.convert("L"))
