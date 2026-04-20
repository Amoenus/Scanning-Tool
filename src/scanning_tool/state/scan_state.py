"""Scan state management."""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo
from scanning_tool.domain.capture import ScanResult


ContinuousModeListener = Callable[[bool], None]


@dataclass
class ScanState:
    """Manages the lifecycle state of the ongoing scan process."""

    is_scanning: bool = False
    continuous_mode: bool = False
    last_result: Optional[ScanResult] = None
    anchor_tracker: Optional["AnchorRegionTracker"] = None
    last_alignment_info: AlignmentInfo = field(default_factory=AlignmentInfo)
    _continuous_mode_listeners: list[ContinuousModeListener] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def add_continuous_mode_listener(self, listener: ContinuousModeListener) -> None:
        self._continuous_mode_listeners.append(listener)

    def set_continuous_mode(self, enabled: bool) -> None:
        if self.continuous_mode == enabled:
            return
        self.continuous_mode = enabled
        self._notify_continuous_mode_listeners()

    def _notify_continuous_mode_listeners(self) -> None:
        for listener in tuple(self._continuous_mode_listeners):
            listener(self.continuous_mode)
