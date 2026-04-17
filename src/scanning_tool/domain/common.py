from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict, TypeAlias

OreTier = Literal["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


class MssMonitor(TypedDict):
    """Monitor dict compatible with the mss library."""

    left: int
    top: int
    width: int
    height: int


@dataclass
class Offset2D:
    """A 2D offset with x and y components."""

    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class OreValueInfo:
    """Tier classification and display color for an ore."""

    tier: OreTier
    color: str


@dataclass
class OreTableEntry:
    """A row in a per-region deposit table, ready for display or serialization."""

    name: str
    prob: str
    min: str
    max: str
    med: str
    tier: OreTier
    color: str


DepositTable = list[OreTableEntry]
RegionDepositTables: TypeAlias = dict[str, dict[str, DepositTable]]
