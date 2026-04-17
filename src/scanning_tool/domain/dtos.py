"""Domain DTOs for raw external data shapes."""

from __future__ import annotations

from typing import Mapping, TypedDict

JsonObject = Mapping[str, object]


class ScanSignatureCSVRowData(TypedDict, total=False):
    """Typed shape for one row of scan signature CSV input."""

    mineral: str
    category: str
    base_value: str | int | float
    max_multiplier: str | int | float


class OreStatisticsData(TypedDict, total=False):
    prob: float | str
    minPct: float | str
    maxPct: float | str
    medPct: float | str


class DepositData(TypedDict, total=False):
    users: int | str
    scans: int | str
    clusters: int | str
    clusterCount: Mapping[str, float]
    mass: Mapping[str, float]
    inst: Mapping[str, float]
    res: Mapping[str, float]
    ores: Mapping[str, OreStatisticsData]


RegionData = Mapping[str, DepositData]
RockDataJSON = Mapping[str, RegionData]
