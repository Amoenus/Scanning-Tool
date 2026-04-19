from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError, field_validator

from scanning_tool.domain.dtos import JsonObject
from scanning_tool.domain.parsers import parse_float, parse_int


class OreStatisticsSchema(BaseModel):
    prob: float = 0.0
    minPct: float = 0.0
    maxPct: float = 0.0
    medPct: float = 0.0

    model_config = {"extra": "ignore"}

    @field_validator("*", mode="before")
    @classmethod
    def _coerce_to_float(cls, value):
        parsed_value = parse_float(value)
        return parsed_value if parsed_value is not None else 0.0

    def to_domain(self) -> "OreStatistics":
        return OreStatistics(
            prob=self.prob,
            minPct=self.minPct,
            maxPct=self.maxPct,
            medPct=self.medPct,
        )


class DepositSchema(BaseModel):
    users: int = 0
    scans: int = 0
    clusters: int = 0
    clusterCount: dict[str, float] = Field(default_factory=dict)
    mass: dict[str, float] = Field(default_factory=dict)
    inst: dict[str, float] = Field(default_factory=dict)
    res: dict[str, float] = Field(default_factory=dict)
    ores: dict[str, OreStatisticsSchema] = Field(default_factory=dict)

    model_config = {"extra": "ignore"}

    @field_validator("users", "scans", "clusters", mode="before")
    @classmethod
    def _coerce_to_int(cls, value):
        parsed_value = parse_int(value)
        return parsed_value if parsed_value is not None else 0

    @field_validator("clusterCount", "mass", "inst", "res", mode="before")
    @classmethod
    def _coerce_float_mapping(cls, value):
        if not isinstance(value, dict):
            return {}

        converted: dict[str, float] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            parsed_value = parse_float(raw_value)
            if parsed_value is None:
                continue
            converted[raw_key] = parsed_value
        return converted


@dataclass
class OreStatistics:
    """Per-ore stats inside a Deposit's `ores` map (loaded from RockType.json)."""

    prob: float
    minPct: float
    maxPct: float
    medPct: float

    @classmethod
    def from_dict(cls, data: JsonObject) -> "OreStatistics":
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
    def from_dict(cls, data: JsonObject) -> "Deposit":
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
    def from_dict(cls, data: JsonObject) -> "Region":
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
    def from_dict(cls, data: JsonObject) -> "RockDataCollection":
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
