import pytest
from scanning_tool.domain.models import Deposit, Region, RockDataCollection, OreStatistics

def test_ore_statistics_from_dict():
    data = {
        "prob": 0.5,
        "minPct": 0.1,
        "maxPct": 0.9,
        "medPct": 0.5
    }
    stats = OreStatistics.from_dict(data)
    assert stats.prob == 0.5
    assert stats.minPct == 0.1
    assert stats.maxPct == 0.9
    assert stats.medPct == 0.5

    # Test fallback parsing
    bad_data = {
        "prob": "0.5",
        "missing_keys": True
    }
    stats = OreStatistics.from_dict(bad_data)
    assert stats.prob == 0.5
    assert stats.minPct == 0.0

def test_deposit_from_dict():
    data = {
        "users": 10,
        "scans": 20,
        "clusters": 5,
        "ores": {
            "IRON": {
                "prob": 0.8
            }
        }
    }
    deposit = Deposit.from_dict(data)
    assert deposit.users == 10
    assert deposit.scans == 20
    assert "IRON" in deposit.ores
    assert deposit.ores["IRON"].prob == 0.8

def test_rock_data_collection_from_dict():
    data = {
        "STANTON": {
            "CTYPE": {
                "users": 289,
                "ores": {
                    "GOLD": {
                        "prob": 0.1
                    }
                }
            }
        }
    }
    collection = RockDataCollection.from_dict(data)
    assert "STANTON" in collection.regions
    assert "CTYPE" in collection.regions["STANTON"].deposits
    assert collection.regions["STANTON"].deposits["CTYPE"].users == 289
