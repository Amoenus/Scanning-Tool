from __future__ import annotations

from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest
from scanning_tool.interfaces.capture import AlignmentAdapter
from scanning_tool.services.alignment_service import alignment_service


class UIAlignmentAdapter(AlignmentAdapter):
    """Adapter that forwards alignment requests to the service."""

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
        )
