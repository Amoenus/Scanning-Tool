"""Compatibility wrapper for legacy domain model imports.

This module preserves old import paths while routing users to the
new explicit domain submodules.
"""

from scanning_tool.domain.alignment import AlignmentInfo, AlignmentRequest, AnchorDetection, CaptureRegion
from scanning_tool.domain.capture import CodeExtraction, DepositInfo, ScanResult
from scanning_tool.domain.common import (
    DepositTable,
    MssMonitor,
    Offset2D,
    OreTableEntry,
    OreTier,
    OreValueInfo,
    RegionDepositTables,
)
from scanning_tool.domain.dtos import DepositData, OreStatisticsData, RegionData, RockDataJSON, ScanSignatureCSVRowData
from scanning_tool.domain.ore import Deposit, OreStatistics, OreTierInfo, Region, RockData, RockDataCollection
from scanning_tool.domain.scan_signature import ScanSignature, ScanSignatureCSVRow, SignatureRegistry

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
