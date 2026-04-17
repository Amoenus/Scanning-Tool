from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

from scanning_tool.domain.alignment import AlignmentInfo, CaptureRegion
from scanning_tool.domain.capture import DepositInfo, ScanResult
from scanning_tool.domain.common import MssMonitor, OreTableEntry

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
    selected_region: str
    info: Optional[DepositInfo]
    code: Optional[str]
    code_raw: Optional[str]
    raw_text: Optional[str]
    table: Optional[DepositTable]

    def to_dict(self) -> StatusResponseDict:
        return {
            "region": self._capture_region_dict(self.region),
            "label_color": self.label_color,
            "last": self._scan_result_dict(self.last),
            "alignment": self._alignment_info_dict(self.alignment),
            "selected_region": self.selected_region,
            "info": self._deposit_info_dict(self.info),
            "code": self.code,
            "code_raw": self.code_raw,
            "raw_text": self.raw_text,
            "table": self._deposit_table(self.table),
        }

    @staticmethod
    def _capture_region_dict(region: CaptureRegion) -> MssMonitor:
        return {
            "left": region.left,
            "top": region.top,
            "width": region.width,
            "height": region.height,
        }

    @staticmethod
    def _deposit_info_dict(info: Optional[DepositInfo]) -> DepositInfoDict | None:
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

    @classmethod
    def _scan_result_dict(cls, result: Optional[ScanResult]) -> ScanResultDict | None:
        if result is None:
            return None
        return {
            "label": result.label,
            "region": cls._capture_region_dict(result.region),
            "info": cls._deposit_info_dict(result.info),
            "code_raw": result.code_raw,
            "raw_text": result.raw_text,
        }

    @staticmethod
    def _alignment_info_dict(alignment: AlignmentInfo) -> AlignmentInfoDict:
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

    @staticmethod
    def _ore_table_entry_dict(entry: OreTableEntry) -> OreTableEntryDict:
        return {
            "name": entry.name,
            "prob": entry.prob,
            "min": entry.min,
            "max": entry.max,
            "med": entry.med,
            "tier": entry.tier,
            "color": entry.color,
        }

    @classmethod
    def _deposit_table(cls, table: Optional[DepositTable]) -> list[OreTableEntryDict] | None:
        if table is None:
            return None
        return [cls._ore_table_entry_dict(entry) for entry in table]
