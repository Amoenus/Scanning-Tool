from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from scanning_tool.domain.alignment import AlignmentInfo, CaptureRegion
from scanning_tool.domain.capture import DepositInfo, ScanResult
from scanning_tool.domain.common import OreTableEntry

DepositTable = list[OreTableEntry]


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

    def to_dict(self) -> dict:
        return asdict(self)
