"""Compatibility wrapper for legacy domain model imports.

This module preserves old import paths while routing users to the
new explicit domain submodules.
"""

from .alignment import *
from .capture import *
from .common import *
from .ore import *
from .scan_signature import *
from .dtos import *

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
