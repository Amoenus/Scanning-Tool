"""Web payload type definitions and response models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

from scanning_tool.domain.alignment import AlignmentInfo, CaptureRegion
from scanning_tool.domain.capture import DepositInfo, ScanResult
from scanning_tool.domain.common import MssMonitor, OreTableEntry, SpaceSystem

DepositTable = list[OreTableEntry]
OreTier = Literal["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


class DepositInfoDict(TypedDict):
    key: str | None
    name: str | None
    category: str | None
    type: str | None
    id: str | int | None
    base_code: int | None
    deposits: int | None
    max_multiplier: int | None


class ScanResultDict(TypedDict):
    label: str
    region: MssMonitor
    info: DepositInfoDict | None
    code_raw: str | None
    raw_text: str | None


class AlignmentInfoDict(TypedDict):
    enabled: bool
    matched: bool
    template: str | None
    score: float
    match_left: int | None
    match_top: int | None
    capture_left: int | None
    capture_top: int | None


class OreTableEntryDict(TypedDict):
    name: str
    prob: str
    min: str
    max: str
    med: str
    tier: OreTier
    color: str


class StatusResponseDict(TypedDict):
    region: MssMonitor
    label_color: str
    last: ScanResultDict | None
    alignment: AlignmentInfoDict
    selected_region: str
    info: DepositInfoDict | None
    code: str | None
    code_raw: str | None
    raw_text: str | None
    table: list[OreTableEntryDict] | None


@dataclass
class StatusResponse:
    """Payload returned by the /status web endpoint."""

    region: CaptureRegion
    label_color: str
    last: Optional[ScanResult]
    alignment: AlignmentInfo
    selected_region: SpaceSystem
    info: Optional[DepositInfo]
    code: Optional[str]
    code_raw: Optional[str]
    raw_text: Optional[str]
    table: Optional[DepositTable]

    def to_dict(self) -> StatusResponseDict:
        from scanning_tool.web.schemas.serializers import StatusResponseSerializer

        return StatusResponseSerializer.to_dict(self)
