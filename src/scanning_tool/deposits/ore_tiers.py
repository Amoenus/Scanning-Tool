"""Ore tier definitions and value mappings."""

from scanning_tool.domain.common import OreTier, OreValueInfo
from scanning_tool.domain.ore import OreTierInfo

ORE_TIERS: dict[OreTier, OreTierInfo] = {
    "HIGHEST": OreTierInfo(ores=["QUANTANIUM", "STILERON", "RICCITE"], color="#E88AFF"),
    "HIGH": OreTierInfo(ores=["TARANITE", "BEXALITE", "GOLD"], color="#63E64C"),
    "MEDIUM": OreTierInfo(
        ores=["LARANITE", "BORASE", "BERYL", "AGRICIUM", "HEPHAESTANITE"],
        color="#E6E14C",
    ),
    "LOW": OreTierInfo(
        ores=[
            "TUNGSTEN",
            "TITANIUM",
            "SILICON",
            "IRON",
            "QUARTZ",
            "CORUNDUM",
            "COPPER",
            "TIN",
            "ALUMINUM",
            "ICE",
        ],
        color="#E69E4C",
    ),
}

ORE_VALUE_MAP: dict[str, OreValueInfo] = {}
for _tier, _data in ORE_TIERS.items():
    for _ore in _data.ores:
        ORE_VALUE_MAP[_ore.upper()] = OreValueInfo(tier=_tier, color=_data.color)

TIER_ORDER: list[OreTier] = ["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]
