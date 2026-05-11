from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.interfaces.capture import AlignmentAdapter
from scanning_tool.services.alignment_service import alignment_service

if TYPE_CHECKING:
    from scanning_tool.core.anchor import AnchorRegionTracker
    from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest


class UIAlignmentAdapter(AlignmentAdapter):
    """Adapter that forwards alignment requests to the service."""

    def align(
        self,
        anchor_tracker: AnchorRegionTracker | None,
        last_alignment_info: AlignmentInfo,
        alignment_request: AlignmentRequest,
    ) -> bool:
        """Forward alignment request to the alignment service.

        Parameters
        ----------
        anchor_tracker : AnchorRegionTracker | None
            The anchor region tracker instance.
        last_alignment_info : AlignmentInfo
            The last alignment information.
        alignment_request : AlignmentRequest
            The alignment request to process.

        Returns
        -------
        bool
            True if alignment was successful, False otherwise.

        """
        return alignment_service.align(
            anchor_tracker,
            last_alignment_info,
            alignment_request,
        )
