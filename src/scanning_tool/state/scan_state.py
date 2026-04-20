"""Scan state management."""

from dataclasses import dataclass, field
from typing import Callable, Optional
from blinker import Signal
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
    _continuous_mode_signal: Signal = field(default_factory=Signal, init=False, repr=False)
    _scan_result_signal: Signal = field(default_factory=Signal, init=False, repr=False)
    _alignment_info_signal: Signal = field(default_factory=Signal, init=False, repr=False)

    @property
    def last_result(self) -> Optional[ScanResult]:
        return self._last_result

    @last_result.setter
    def last_result(self, value: Optional[ScanResult]) -> None:
        self._last_result = value
        self._notify_scan_result_listeners()

    def add_continuous_mode_listener(self, listener: ContinuousModeListener) -> None:
        def receiver(sender: object, continuous_mode: bool) -> None:
            listener(continuous_mode)

        self._continuous_mode_signal.connect(receiver, weak=False)

    def add_scan_result_listener(self, listener: ScanResultListener) -> None:
        def receiver(sender: object, scan_result: Optional[ScanResult]) -> None:
            listener(scan_result)

        self._scan_result_signal.connect(receiver, weak=False)

    def add_alignment_info_listener(self, listener: AlignmentInfoListener) -> None:
        def receiver(sender: object, alignment_info: AlignmentInfo) -> None:
            listener(alignment_info)

        self._alignment_info_signal.connect(receiver, weak=False)

    def set_continuous_mode(self, enabled: bool) -> None:
        if self.continuous_mode == enabled:
            return
        self.continuous_mode = enabled
        self._notify_continuous_mode_listeners()

    def notify_alignment_info_listeners(self) -> None:
        self._alignment_info_signal.send(self, alignment_info=self.last_alignment_info)

    def _notify_continuous_mode_listeners(self) -> None:
        self._continuous_mode_signal.send(self, continuous_mode=self.continuous_mode)

    def _notify_scan_result_listeners(self) -> None:
        self._scan_result_signal.send(self, scan_result=self.last_result)
