"""Web payload serializer implementations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AlignmentInfo, CaptureRegion
    from scanning_tool.domain.capture import DepositInfo, ScanResult
    from scanning_tool.domain.common import MssMonitor, OreTableEntry

from scanning_tool.web.schemas.types import (
        AlignmentInfoDict,
        DepositInfoDict,
        DepositTable,
        OreTableEntryDict,
        ScanResultDict,
        StatusResponse,
        StatusResponseDict,
    )
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
    def to_dict(info: DepositInfo | None) -> DepositInfoDict | None:
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
    def to_dict(cls, result: ScanResult | None) -> ScanResultDict | None:
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
    def to_dict(cls, table: DepositTable | None) -> list[OreTableEntryDict] | None:
        if table is None:
            return None
        return [OreTableEntrySerializer.to_dict(entry) for entry in table]


class StatusResponseSerializer:
    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.replace(microsecond=0).isoformat() + "Z"

    @classmethod
    def to_dict(cls, status_response: StatusResponse) -> StatusResponseDict:
        return {
            "region": CaptureRegionSerializer.to_dict(status_response.region),
            "label_color": status_response.label_color,
            "last": ScanResultSerializer.to_dict(status_response.last),
            "alignment": AlignmentInfoSerializer.to_dict(status_response.alignment),
            "selected_region": status_response.selected_region.value,
            "status": status_response.status,
            "updated_at": cls._format_datetime(status_response.updated_at),
            "info": DepositInfoSerializer.to_dict(status_response.info),
            "code": status_response.code,
            "code_raw": status_response.code_raw,
            "raw_text": status_response.raw_text,
            "table": DepositTableSerializer.to_dict(status_response.table),
        }
