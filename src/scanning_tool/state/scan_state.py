"""Scan state management."""


from dataclasses import dataclass, field
from typing import Optional
from scanning_tool.core.AnchorRegionTracker import AnchorRegionTracker
from scanning_tool.domain.models import AlignmentInfo, ScanResult

@dataclass
class ScanState:
    """Manages the lifecycle state of the ongoing scan process."""
    is_scanning: bool = False
    continuous_mode: bool = False
    last_result: Optional[ScanResult] = None
    anchor_tracker: Optional[AnchorRegionTracker] = None
    last_alignment_info: AlignmentInfo = field(default_factory=AlignmentInfo)
