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


class CaptureRegionSerializer:
    @staticmethod
    def to_dict(region: CaptureRegion) -> MssMonitor:
        return {
            "left": region.left,
            "top": region.top,
            "width": region.width,
            "height": region.height,
        }


class DepositInfoSerializer:
    @staticmethod
    def to_dict(info: Optional[DepositInfo]) -> DepositInfoDict | None:
        if info is None:
            return None
        return {
            "key": info.key,
            "name": info.name,
            "category": info.category,
            "type": info.type,
            "id": info.id,
            "base_code": info.base_code,
            "deposits": info.deposits,
            "max_multiplier": info.max_multiplier,
        }


class ScanResultSerializer:
    @classmethod
    def to_dict(cls, result: Optional[ScanResult]) -> ScanResultDict | None:
        if result is None:
            return None
        return {
            "label": result.label,
            "region": CaptureRegionSerializer.to_dict(result.region),
            "info": DepositInfoSerializer.to_dict(result.info),
            "code_raw": result.code_raw,
            "raw_text": result.raw_text,
        }


class AlignmentInfoSerializer:
    @staticmethod
    def to_dict(alignment: AlignmentInfo) -> AlignmentInfoDict:
        return {
            "enabled": alignment.enabled,
            "matched": alignment.matched,
            "template": alignment.template,
            "score": alignment.score,
            "match_left": alignment.match_left,
            "match_top": alignment.match_top,
            "capture_left": alignment.capture_left,
            "capture_top": alignment.capture_top,
        }


class OreTableEntrySerializer:
    @staticmethod
    def to_dict(entry: OreTableEntry) -> OreTableEntryDict:
        return {
            "name": entry.name,
            "prob": entry.prob,
            "min": entry.min,
            "max": entry.max,
            "med": entry.med,
            "tier": entry.tier,
            "color": entry.color,
        }


class DepositTableSerializer:
    @classmethod
    def to_dict(cls, table: Optional[DepositTable]) -> list[OreTableEntryDict] | None:
        if table is None:
            return None
        return [OreTableEntrySerializer.to_dict(entry) for entry in table]


class StatusResponseSerializer:
    @classmethod
    def to_dict(cls, status_response: "StatusResponse") -> StatusResponseDict:
        return {
            "region": CaptureRegionSerializer.to_dict(status_response.region),
            "label_color": status_response.label_color,
            "last": ScanResultSerializer.to_dict(status_response.last),
            "alignment": AlignmentInfoSerializer.to_dict(status_response.alignment),
            "selected_region": status_response.selected_region.value,
            "info": DepositInfoSerializer.to_dict(status_response.info),
            "code": status_response.code,
            "code_raw": status_response.code_raw,
            "raw_text": status_response.raw_text,
            "table": DepositTableSerializer.to_dict(status_response.table),
        }


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
        return StatusResponseSerializer.to_dict(self)
