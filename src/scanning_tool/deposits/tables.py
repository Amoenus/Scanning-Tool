"""Build deposit ore tables from rock data."""

import json
from typing import Dict

from scanning_tool.config import ROCK_TYPE_FILE
from scanning_tool.domain.common import DepositTable, OreTableEntry, OreValueInfo, SpaceSystem
from scanning_tool.state.service_state import ServiceState
from scanning_tool.domain.ore import Deposit, Region, OreStatistics, RockDataCollection
from scanning_tool.deposits.ore_tiers import ORE_VALUE_MAP, TIER_ORDER


class DepositTableBuilder:
    """Build deposit ore tables from rock data."""

    def build_deposit_tables(self, region: Region) -> Dict[str, DepositTable]:
        deposit_tables: Dict[str, DepositTable] = {}
        for deposit_name, deposit in region.deposits.items():
            table = self._build_deposit_table(deposit)
            table.sort(key=lambda entry: TIER_ORDER.index(entry.tier))
            deposit_tables[deposit_name.upper()] = table
        return deposit_tables

    def _build_deposit_table(self, deposit: Deposit) -> DepositTable:
        return [
            self._create_ore_table_entry(ore_name, ore_stats)
            for ore_name, ore_stats in deposit.ores.items()
        ]

    def _create_ore_table_entry(self, ore_name: str, stats: OreStatistics) -> OreTableEntry:
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
    return DepositTableBuilder().build_deposit_tables(region)


def _create_ore_table_entry(ore_name: str, stats: OreStatistics) -> OreTableEntry:
    return DepositTableBuilder()._create_ore_table_entry(ore_name, stats)


def load_rock_data(service_state: ServiceState) -> None:
    """Load RockType.json and build deposit tables into service state."""
    with ROCK_TYPE_FILE.open("r") as f:
        raw_data = json.load(f)
        service_state.rocks.rock_data = RockDataCollection.from_dict(raw_data)

    service_state.rocks.deposit_tables = {
        SpaceSystem.normalize(region_name): build_deposit_tables(region_data)
        for region_name, region_data in service_state.rocks.rock_data.regions.items()
    }
