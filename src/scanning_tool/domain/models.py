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
from .dtos import (
    DepositData,
    OreStatisticsData,
    RegionData,
    RockDataJSON,
    ScanSignatureCSVRowData,
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

__all__ = [
    "AlignmentInfo",
    "AlignmentRequest",
    "AnchorDetection",
    "CaptureRegion",
    "CodeExtraction",
    "Deposit",
    "DepositData",
    "DepositInfo",
    "DepositTable",
    "MssMonitor",
    "Offset2D",
    "OreStatistics",
    "OreStatisticsData",
    "OreTableEntry",
    "OreTier",
    "OreTierInfo",
    "OreValueInfo",
    "Region",
    "RegionData",
    "RegionDepositTables",
    "RockData",
    "RockDataCollection",
    "RockDataJSON",
    "ScanResult",
    "ScanSignature",
    "ScanSignatureCSVRow",
    "ScanSignatureCSVRowData",
    "SignatureRegistry",
]
