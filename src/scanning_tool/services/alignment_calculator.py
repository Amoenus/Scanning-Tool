from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AnchorDetection, CaptureRegion
    from scanning_tool.domain.common import Offset2D
class AlignmentCalculator:
    @staticmethod
    def calculate_aligned_position(
        detection: AnchorDetection,
        capture_region: CaptureRegion,
        anchor_offset: Offset2D,
    ) -> tuple[int, int]:
        base_left = (
            detection.match_left
            + (detection.template_width / 2.0)
            - (capture_region.width / 2.0)
        )
        base_top = (
            detection.match_top
            + (detection.template_height / 2.0)
            - (capture_region.height / 2.0)
        )
        new_left = int(round(base_left + anchor_offset.x))
        new_top = int(round(base_top + anchor_offset.y))
        return new_left, new_top
