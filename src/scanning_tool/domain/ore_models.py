from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import ValidationError

from scanning_tool.domain.dtos import JsonObject
from scanning_tool.domain.ore_schemas import DepositSchema, OreStatisticsSchema


@dataclass
class OreStatistics:
    """Per-ore stats inside a Deposit's `ores` map (loaded from RockType.json)."""

    prob: float
    minPct: float
    maxPct: float
    medPct: float

    @classmethod
    def from_dict(cls, data: JsonObject) -> OreStatistics:
        try:
            validated = OreStatisticsSchema.model_validate(data)
        except ValidationError:
            validated = OreStatisticsSchema()
        return validated.to_domain()


@dataclass
class Deposit:
    """A single deposit entry inside a region in RockType.json."""

    users: int
    scans: int
    clusters: int
    clusterCount: dict[str, float]
    mass: dict[str, float]
    inst: dict[str, float]
    res: dict[str, float]
    ores: dict[str, OreStatistics]

    @classmethod
    def from_dict(cls, data: JsonObject) -> Deposit:
        try:
            validated = DepositSchema.model_validate(data)
        except ValidationError:
            validated = DepositSchema()

        ores = {
            ore_name: ore_schema.to_domain()
            for ore_name, ore_schema in validated.ores.items()
        }

        return cls(
            users=validated.users,
            scans=validated.scans,
            clusters=validated.clusters,
            clusterCount=validated.clusterCount,
            mass=validated.mass,
            inst=validated.inst,
            res=validated.res,
            ores=ores,
        )


@dataclass
class Region:
    """A collection of deposits for a given region."""

    deposits: dict[str, Deposit]

    @classmethod
    def from_dict(cls, data: JsonObject) -> Region:
        deposits = {
            deposit_name: Deposit.from_dict(deposit_data)
            for deposit_name, deposit_data in data.items()
            if isinstance(deposit_data, dict)
        }
        return cls(deposits=deposits)


@dataclass
class RockDataCollection:
    """Top-level container for all region data."""

    regions: dict[str, Region] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: JsonObject) -> RockDataCollection:
        regions = {
            region_name: Region.from_dict(region_data)
            for region_name, region_data in data.items()
            if isinstance(region_data, dict)
        }
        return cls(regions=regions)


RockData = RockDataCollection  # Alias for backward compatibility during refactor


@dataclass
class OreTierInfo:
    """Ores belonging to a tier plus its display color."""

    ores: list[str]
    color: str


__all__ = [
    "Deposit",
    "OreStatistics",
    "OreTierInfo",
    "Region",
    "RockData",
    "RockDataCollection",
]
