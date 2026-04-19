from __future__ import annotations

from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest
from scanning_tool.interfaces.capture import AlignmentAdapter, SyncCallback
from scanning_tool.services.alignment_service import alignment_service


class UIAlignmentAdapter(AlignmentAdapter):
    """Adapter that forwards alignment requests and GUI sync callbacks to the service."""

    def __init__(
        self,
        sync_capture_sliders: SyncCallback,
        update_capture_overlay_region: SyncCallback,
    ) -> None:
        self._sync_capture_sliders = sync_capture_sliders
        self._update_capture_overlay_region = update_capture_overlay_region

    def align(
        self,
        anchor_tracker: AnchorRegionTracker | None,
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
    ) -> bool:
        return alignment_service.align(
            anchor_tracker,
            last_alignment_info,
            alignment_request,
            self._sync_capture_sliders,
            self._update_capture_overlay_region,
        )
