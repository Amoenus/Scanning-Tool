"""Pure overlay geometry helpers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..layout import AnchorOverlayGeometry, CaptureOverlayLayout, InfoOverlayLayout
from .base import (
    ANCHOR_OVERLAY_PAD,
    CAPTURE_OVERLAY_PADDING_X,
    CAPTURE_OVERLAY_PADDING_Y,
    INFO_OVERLAY_HEIGHT,
    MAX_INFO_OVERLAY_WIDTH,
    MIN_INFO_OVERLAY_WIDTH,
    SCREEN_MARGIN,
)

if TYPE_CHECKING:
    from scanning_tool.config.models import OverlayConfig
    from scanning_tool.domain.alignment import CaptureRegion
def compute_info_overlay_geometry(
    screen_width: int,
    screen_height: int,
    overlay_config: OverlayConfig,
) -> InfoOverlayLayout:
    overlay_width = max(
        MIN_INFO_OVERLAY_WIDTH,
        min(MAX_INFO_OVERLAY_WIDTH, screen_width - SCREEN_MARGIN),
    )
    overlay_height = INFO_OVERLAY_HEIGHT
    base_left = max(0, (screen_width - overlay_width) // 2)
    base_top = max(0, int(screen_height * 0.35) - overlay_height // 2)

    offset_x = overlay_config.info_offset.x
    offset_y = overlay_config.info_offset.y

    max_left = max(0, screen_width - overlay_width)
    max_top = max(0, screen_height - overlay_height)

    left = min(max(0, base_left + offset_x), max_left)
    top = min(max(0, base_top + offset_y), max_top)
    return InfoOverlayLayout(
        width=overlay_width, height=overlay_height, left=left, top=top,
    )


def compute_capture_overlay_layout(
    capture_region: CaptureRegion,
) -> CaptureOverlayLayout:
    cap_w = int(capture_region.width)
    cap_h = int(capture_region.height)

    overlay_width = cap_w + CAPTURE_OVERLAY_PADDING_X
    overlay_height = cap_h + CAPTURE_OVERLAY_PADDING_Y
    left = int(capture_region.left) - (CAPTURE_OVERLAY_PADDING_X // 2)
    top = int(capture_region.top) - CAPTURE_OVERLAY_PADDING_Y

    return CaptureOverlayLayout(
        overlay_width=overlay_width,
        overlay_height=overlay_height,
        left=left,
        top=top,
        padding_x=CAPTURE_OVERLAY_PADDING_X,
        padding_y=CAPTURE_OVERLAY_PADDING_Y,
        cap_w=cap_w,
        cap_h=cap_h,
    )


def compute_anchor_overlay_geometry(
    anchor_region: CaptureRegion,
) -> AnchorOverlayGeometry:
    width = int(anchor_region.width) + ANCHOR_OVERLAY_PAD
    height = int(anchor_region.height) + ANCHOR_OVERLAY_PAD
    left = int(anchor_region.left) - (ANCHOR_OVERLAY_PAD // 2)
    top = int(anchor_region.top) - (ANCHOR_OVERLAY_PAD // 2)

    return AnchorOverlayGeometry(
        width=width,
        height=height,
        left=left,
        top=top,
    )
