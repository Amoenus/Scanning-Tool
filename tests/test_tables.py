from scanning_tool.deposits.tables import _create_ore_table_entry, build_deposit_tables
from scanning_tool.domain.models import (
    Deposit,
    OreStatistics,
    Region,
)


def test_create_ore_table_entry():
    stats = OreStatistics(prob=0.8, minPct=0.1, maxPct=0.9, medPct=0.5)
    entry = _create_ore_table_entry("Gold", stats)

    assert entry.name == "Gold"
    assert entry.prob == "80%"
    assert entry.min == "10%"
    assert entry.max == "90%"
    assert entry.med == "50%"
    assert entry.tier == "HIGH"  # Assuming gold maps to HIGHEST in ORE_VALUE_MAP
    assert entry.color != "#888"  # Should get a valid color from map


def test_build_deposit_tables():
    deposit = Deposit(
        users=1,
        scans=1,
        clusters=1,
        clusterCount={},
        mass={},
        inst={},
        res={},
        ores={"GOLD": OreStatistics(prob=0.5, minPct=0.1, maxPct=0.9, medPct=0.5)},
    )
    region = Region(deposits={"CTYPE": deposit})

    tables = build_deposit_tables(region)
    assert "CTYPE" in tables
    assert len(tables["CTYPE"]) == 1
    assert tables["CTYPE"][0].name == "Gold"
    assert tables["CTYPE"][0].prob == "50%"
