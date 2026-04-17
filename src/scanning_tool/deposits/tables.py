"""Build deposit ore tables from rock data."""

import json
from typing import Dict

from scanning_tool.config import ROCK_TYPE_FILE
from scanning_tool.core.state_manager import service_state
from scanning_tool.domain.models import DepositTable, OreTableEntry, RockDeposit, OreValueInfo
from scanning_tool.deposits.ore_tiers import ORE_VALUE_MAP, TIER_ORDER


def build_deposit_tables(rock_data: Dict[str, RockDeposit]) -> Dict[str, DepositTable]:
    """Build per-deposit ore tables for one region's rock data."""
    deposit_tables: Dict[str, DepositTable] = {}
    for deposit_name, details in rock_data.items():
        ores = details.get("ores", {})
        table: DepositTable = []
        for ore_name, ore_data in ores.items():
            name_up = ore_name.upper()
            value_info = ORE_VALUE_MAP.get(name_up, OreValueInfo(tier="OTHER", color="#888"))
            entry = OreTableEntry(
                name=ore_name.title(),
                prob=f"{ore_data.get('prob', 0) * 100:.0f}%",
                min=f"{ore_data.get('minPct', 0) * 100:.0f}%",
                max=f"{ore_data.get('maxPct', 0) * 100:.0f}%",
                med=f"{ore_data.get('medPct', 0) * 100:.0f}%",
                tier=value_info.tier,
                color=value_info.color,
            )
            table.append(entry)
        table.sort(key=lambda x: TIER_ORDER.index(x.tier))
        deposit_tables[deposit_name.upper()] = table
    return deposit_tables


def load_rock_data() -> None:
    """Load RockType.json and build deposit tables into service state."""
    with open(ROCK_TYPE_FILE, "r") as f:
        service_state.rock_data = json.load(f)

    service_state.deposit_tables = {
        region_name.upper(): build_deposit_tables(region_data)
        for region_name, region_data in service_state.rock_data.items()
    }
