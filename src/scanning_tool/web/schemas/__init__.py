"""Web payload schema package."""

from scanning_tool.web.schemas.serializers import (
    CaptureRegionSerializer,
    DepositInfoSerializer,
    DepositTableSerializer,
    OreTableEntrySerializer,
    ScanResultSerializer,
    StatusResponseSerializer,
)
from scanning_tool.web.schemas.types import (
    DepositInfoDict,
    DepositTable,
    OreTableEntryDict,
    OreTier,
    ScanResultDict,
    StatusResponse,
    StatusResponseDict,
)

__all__ = [
    "CaptureRegionSerializer",
    "DepositInfoDict",
    "DepositInfoSerializer",
    "DepositTable",
    "DepositTableSerializer",
    "OreTableEntryDict",
    "OreTableEntrySerializer",
    "OreTier",
    "ScanResultDict",
    "ScanResultSerializer",
    "StatusResponse",
    "StatusResponseDict",
    "StatusResponseSerializer",
]
