"""Build deposit ore tables from rock data."""

import json
from typing import Dict

from scanning_tool.config import ROCK_TYPE_FILE
from scanning_tool.core.state_manager import service_state
from scanning_tool.domain.models import DepositTable, OreInfo, OreInfoModel, OreTableEntry, RockDeposit, OreValueInfo
from scanning_tool.deposits.ore_tiers import ORE_VALUE_MAP, TIER_ORDER


def _build_ore_table_entry(ore_name: str, ore_data: OreInfo) -> OreTableEntry:
    ore_info = OreInfoModel.from_raw(ore_data)
    name_up = ore_name.upper()
    value_info = ORE_VALUE_MAP.get(name_up, OreValueInfo(tier="OTHER", color="#888"))
    return OreTableEntry(
        name=ore_name.title(),
        prob=ore_info.prob_pct,
        min=ore_info.min_pct_str,
        max=ore_info.max_pct_str,
        med=ore_info.med_pct_str,
        tier=value_info.tier,
        color=value_info.color,
    )


def _build_deposit_table(details: RockDeposit) -> DepositTable:
    ores = details.get("ores", {})
    table = [_build_ore_table_entry(ore_name, ore_data) for ore_name, ore_data in ores.items()]
    table.sort(key=lambda x: TIER_ORDER.index(x.tier))
    return table


def build_deposit_tables(rock_data: Dict[str, RockDeposit]) -> Dict[str, DepositTable]:
    """Build per-deposit ore tables for one region's rock data."""
    return {
        deposit_name.upper(): _build_deposit_table(details)
        for deposit_name, details in rock_data.items()
    }


def load_rock_data() -> None:
    """Load RockType.json and build deposit tables into service state."""
    with open(ROCK_TYPE_FILE, "r") as f:
        service_state.rock_data = json.load(f)

    service_state.deposit_tables = {
        region_name.upper(): build_deposit_tables(region_data)
        for region_name, region_data in service_state.rock_data.items()
    }
