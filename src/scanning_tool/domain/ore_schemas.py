from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, ValidationError, field_validator

from scanning_tool.domain.dtos import JsonObject
from scanning_tool.domain.parsers import parse_float, parse_int

if TYPE_CHECKING:
    from scanning_tool.domain.ore_models import OreStatistics


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
        from scanning_tool.domain.ore_models import OreStatistics

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


__all__ = ["OreStatisticsSchema", "DepositSchema"]
