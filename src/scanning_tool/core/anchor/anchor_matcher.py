from scanning_tool.domain.models import AnchorDetection


import cv2
import numpy as np
from mss.models import Monitor


from typing import List, Optional, Tuple


class AnchorMatcher:
    """Find the best anchor template match in a captured image."""

    def find_best_match(
        self, anchor_gray: np.ndarray, templates: List[Tuple[str, np.ndarray]]
    ) -> Tuple[float, Optional[Tuple[int, int]], Optional[Tuple[str, np.ndarray]]]:
        best_score = -1.0
        best_loc: Optional[Tuple[int, int]] = None
        best_template: Optional[Tuple[str, np.ndarray]] = None

        for template_name, template_img in templates:
            if (
                anchor_gray.shape[0] < template_img.shape[0]
                or anchor_gray.shape[1] < template_img.shape[1]
            ):
                continue
            res = cv2.matchTemplate(anchor_gray, template_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_score:
                best_score = float(max_val)
                best_loc = (int(max_loc[0]), int(max_loc[1]))
                best_template = (template_name, template_img)

        return best_score, best_loc, best_template

    def build_detection(
        self,
        monitor: Monitor,
        best_loc: Tuple[int, int],
        best_template: Tuple[str, np.ndarray],
        best_score: float,
    ) -> AnchorDetection:
        match_left = monitor["left"] + best_loc[0]
        match_top = monitor["top"] + best_loc[1]
        return AnchorDetection(
            match_left=float(match_left),
            match_top=float(match_top),
            score=best_score,
            template=best_template[0],
            template_width=float(best_template[1].shape[1]),
            template_height=float(best_template[1].shape[0]),
        )
