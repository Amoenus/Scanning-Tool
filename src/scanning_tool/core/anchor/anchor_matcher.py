from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import cv2
from scanning_tool.domain.alignment import AnchorDetection

if TYPE_CHECKING:
    import numpy as np
    from mss.models import Monitor
    from scanning_tool.core.anchor.anchor_template_loader import AnchorTemplate


class AnchorMatcher:
    """Find the best anchor template match in a captured image."""

    def find_best_match(
        self, anchor_gray: np.ndarray, templates: list[AnchorTemplate]
    ) -> tuple[float, Optional[tuple[int, int]], Optional[AnchorTemplate]]:
        best_score = -1.0
        best_loc: Optional[tuple[int, int]] = None
        best_template: Optional[AnchorTemplate] = None

        for template in templates:
            if (
                anchor_gray.shape[0] < template.image.shape[0]
                or anchor_gray.shape[1] < template.image.shape[1]
            ):
                continue
            res = cv2.matchTemplate(anchor_gray, template.image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_score:
                best_score = float(max_val)
                best_loc = (int(max_loc[0]), int(max_loc[1]))
                best_template = template

        return best_score, best_loc, best_template

    def build_detection(
        self,
        monitor: Monitor,
        best_loc: tuple[int, int],
        best_template: AnchorTemplate,
        best_score: float,
    ) -> AnchorDetection:
        match_left = monitor["left"] + best_loc[0]
        match_top = monitor["top"] + best_loc[1]
        return AnchorDetection(
            match_left=float(match_left),
            match_top=float(match_top),
            score=best_score,
            template=best_template.name,
            template_width=float(best_template.image.shape[1]),
            template_height=float(best_template.image.shape[0]),
        )
