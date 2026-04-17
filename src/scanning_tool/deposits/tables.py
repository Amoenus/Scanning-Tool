"""Build deposit ore tables from rock data."""

import json
from typing import Dict

from scanning_tool.config import ROCK_TYPE_FILE
from scanning_tool.state.manager import service_state
from scanning_tool.domain.models import (
    DepositTable,
    OreTableEntry,
    Region,
    OreStatistics,
    OreValueInfo,
    RockDataCollection,
)
from scanning_tool.deposits.ore_tiers import ORE_VALUE_MAP, TIER_ORDER


def _create_ore_table_entry(ore_name: str, stats: OreStatistics) -> OreTableEntry:
    name_up = ore_name.upper()
    value_info = ORE_VALUE_MAP.get(name_up, OreValueInfo(tier="OTHER", color="#888"))
    return OreTableEntry(
        name=ore_name.title(),
        prob=f"{stats.prob * 100:.0f}%",
        min=f"{stats.minPct * 100:.0f}%",
        max=f"{stats.maxPct * 100:.0f}%",
        med=f"{stats.medPct * 100:.0f}%",
        tier=value_info.tier,
        color=value_info.color,
    )


def build_deposit_tables(region: Region) -> Dict[str, DepositTable]:
    """Build per-deposit ore tables for one region's rock data."""
    deposit_tables: Dict[str, DepositTable] = {}
    for deposit_name, deposit in region.deposits.items():
        table: DepositTable = []
        for ore_name, ore_stats in deposit.ores.items():
            entry = _create_ore_table_entry(ore_name, ore_stats)
            table.append(entry)
        table.sort(key=lambda x: TIER_ORDER.index(x.tier))
        deposit_tables[deposit_name.upper()] = table
    return deposit_tables


def load_rock_data() -> None:
    """Load RockType.json and build deposit tables into service state."""
    with open(ROCK_TYPE_FILE, "r") as f:
        raw_data = json.load(f)
        service_state.rocks.rock_data = RockDataCollection.from_dict(raw_data)

    service_state.rocks.deposit_tables = {
        region_name.upper(): build_deposit_tables(region_data)
        for region_name, region_data in service_state.rocks.rock_data.regions.items()
    }
