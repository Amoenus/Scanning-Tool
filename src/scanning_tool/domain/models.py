"""Compatibility wrapper for legacy domain model imports.

This module preserves old import paths while routing users to the
new explicit domain submodules.
"""

from .alignment import (
    AlignmentInfo,
    AlignmentRequest,
    AnchorDetection,
    CaptureRegion,
)
from .capture import CodeExtraction, DepositInfo, ScanResult
from .common import (
    DepositTable,
    MssMonitor,
    Offset2D,
    OreTableEntry,
    OreTier,
    OreValueInfo,
    RegionDepositTables,
)
from .ore import (
    Deposit,
    OreStatistics,
    OreTierInfo,
    Region,
    RockData,
    RockDataCollection,
)
from .scan_signature import ScanSignature, ScanSignatureCSVRow, SignatureRegistry
from .dtos import (
    DepositData,
    OreStatisticsData,
    RegionData,
    RockDataJSON,
    ScanSignatureCSVRowData,
)

__all__ = [
    "AlignmentInfo",
    "AlignmentRequest",
    "AnchorDetection",
    "CaptureRegion",
    "CodeExtraction",
    "DepositInfo",
    "ScanResult",
    "MssMonitor",
    "Offset2D",
    "OreTier",
    "OreValueInfo",
    "OreTableEntry",
    "DepositTable",
    "RegionDepositTables",
    "OreStatistics",
    "Deposit",
    "Region",
    "RockDataCollection",
    "RockData",
    "OreTierInfo",
    "ScanSignature",
    "ScanSignatureCSVRow",
    "SignatureRegistry",
    "ScanSignatureCSVRowData",
    "OreStatisticsData",
    "DepositData",
    "RegionData",
    "RockDataJSON",
]
