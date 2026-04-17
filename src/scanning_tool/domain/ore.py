from __future__ import annotations

from dataclasses import dataclass, field

from scanning_tool.domain.dtos import JsonObject


@dataclass
class OreStatistics:
    """Per-ore stats inside a Deposit's `ores` map (loaded from RockType.json)."""

    prob: float
    minPct: float
    maxPct: float
    medPct: float

    @staticmethod
    def _to_float(value: int | float | str | None) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    @classmethod
    def from_dict(cls, data: JsonObject) -> "OreStatistics":
        return cls(
            prob=cls._to_float(data.get("prob")),
            minPct=cls._to_float(data.get("minPct")),
            maxPct=cls._to_float(data.get("maxPct")),
            medPct=cls._to_float(data.get("medPct")),
        )


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

    @staticmethod
    def _to_int(value: int | str | float | object | None) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _to_float_mapping(value: object | None) -> dict[str, float]:
        if not isinstance(value, dict):
            return {}

        converted: dict[str, float] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            if isinstance(raw_value, (int, float)):
                converted[raw_key] = float(raw_value)
            elif isinstance(raw_value, str):
                try:
                    converted[raw_key] = float(raw_value)
                except ValueError:
                    continue
        return converted

    @classmethod
    def from_dict(cls, data: JsonObject) -> "Deposit":
        ores_data = data.get("ores", {})
        ores = {
            ore_name: OreStatistics.from_dict(ore_data)
            for ore_name, ore_data in ores_data.items()
            if isinstance(ore_data, dict)
        }

        return cls(
            users=cls._to_int(data.get("users")),
            scans=cls._to_int(data.get("scans")),
            clusters=cls._to_int(data.get("clusters")),
            clusterCount=cls._to_float_mapping(data.get("clusterCount")),
            mass=cls._to_float_mapping(data.get("mass")),
            inst=cls._to_float_mapping(data.get("inst")),
            res=cls._to_float_mapping(data.get("res")),
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
