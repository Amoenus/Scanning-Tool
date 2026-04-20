"""Scan state management."""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentInfo
from scanning_tool.domain.capture import ScanResult


ContinuousModeListener = Callable[[bool], None]
ScanResultListener = Callable[[Optional[ScanResult]], None]
AlignmentInfoListener = Callable[[AlignmentInfo], None]


@dataclass
class ScanState:
    """Manages the lifecycle state of the ongoing scan process."""

    is_scanning: bool = False
    continuous_mode: bool = False
    anchor_tracker: Optional["AnchorRegionTracker"] = None
    last_alignment_info: AlignmentInfo = field(default_factory=AlignmentInfo)
    _last_result: Optional[ScanResult] = field(default=None, init=False, repr=False)
    _continuous_mode_listeners: list[ContinuousModeListener] = field(
        default_factory=list,
        init=False,
        repr=False,
    )
    _scan_result_listeners: list[ScanResultListener] = field(
        default_factory=list,
        init=False,
        repr=False,
    )
    _alignment_info_listeners: list[AlignmentInfoListener] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    @property
    def last_result(self) -> Optional[ScanResult]:
        return self._last_result

    @last_result.setter
    def last_result(self, value: Optional[ScanResult]) -> None:
        self._last_result = value
        self._notify_scan_result_listeners()

    def add_continuous_mode_listener(self, listener: ContinuousModeListener) -> None:
        self._continuous_mode_listeners.append(listener)

    def add_scan_result_listener(self, listener: ScanResultListener) -> None:
        self._scan_result_listeners.append(listener)

    def add_alignment_info_listener(self, listener: AlignmentInfoListener) -> None:
        self._alignment_info_listeners.append(listener)

    def set_continuous_mode(self, enabled: bool) -> None:
        if self.continuous_mode == enabled:
            return
        self.continuous_mode = enabled
        self._notify_continuous_mode_listeners()

    def notify_alignment_info_listeners(self) -> None:
        for listener in tuple(self._alignment_info_listeners):
            listener(self.last_alignment_info)

    def _notify_continuous_mode_listeners(self) -> None:
        for listener in tuple(self._continuous_mode_listeners):
            listener(self.continuous_mode)

    def _notify_scan_result_listeners(self) -> None:
        for listener in tuple(self._scan_result_listeners):
            listener(self.last_result)
