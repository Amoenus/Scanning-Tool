import pytest
from scanning_tool.domain.common import SpaceSystem
from scanning_tool.domain.models import (
    AlignmentInfo,
    AlignmentRequest,
    AnchorDetection,
    CaptureRegion,
    Deposit,
    Offset2D,
    Region,
    RockDataCollection,
    OreStatistics,
)
from scanning_tool.config.service import ConfigData


def test_ore_statistics_from_dict():
    data = {"prob": 0.5, "minPct": 0.1, "maxPct": 0.9, "medPct": 0.5}
    stats = OreStatistics.from_dict(data)
    assert stats.prob == 0.5
    assert stats.minPct == 0.1
    assert stats.maxPct == 0.9
    assert stats.medPct == 0.5

    # Test fallback parsing
    bad_data = {"prob": "0.5", "missing_keys": True}
    stats = OreStatistics.from_dict(bad_data)
    assert stats.prob == 0.5
    assert stats.minPct == 0.0


def test_deposit_from_dict():
    data = {"users": 10, "scans": 20, "clusters": 5, "ores": {"IRON": {"prob": 0.8}}}
    deposit = Deposit.from_dict(data)
    assert deposit.users == 10
    assert deposit.scans == 20
    assert "IRON" in deposit.ores
    assert deposit.ores["IRON"].prob == 0.8


def test_rock_data_collection_from_dict():
    data = {"STANTON": {"CTYPE": {"users": 289, "ores": {"GOLD": {"prob": 0.1}}}}}
    collection = RockDataCollection.from_dict(data)
    assert "STANTON" in collection.regions
    assert "CTYPE" in collection.regions["STANTON"].deposits
    assert collection.regions["STANTON"].deposits["CTYPE"].users == 289


def test_alignment_request_and_info_helpers():
    config = ConfigData()
    request = AlignmentRequest.from_config(config)

    assert request.enabled is True
    assert request.threshold == float(config.anchor_threshold)
    assert request.capture_region is config.capture_region
    assert request.anchor_offset is config.anchor_offset

    info = AlignmentInfo()
    info.matched = True
    info.template = "test"
    info.score = 0.9
    info.match_left = 5
    info.match_top = 10
    info.capture_left = 100
    info.capture_top = 200

    info.reset()
    assert info.matched is False
    assert info.template is None
    assert info.score == 0.0
    assert info.match_left is None
    assert info.match_top is None
    assert info.capture_left is None
    assert info.capture_top is None

    detection = AnchorDetection(
        match_left=12.3,
        match_top=34.5,
        score=0.92,
        template="anchor.png",
        template_width=80.0,
        template_height=40.0,
    )

    info.update_from_detection(detection, request.capture_region)
    assert info.matched is True
    assert info.template == "anchor.png"
    assert info.score == 0.92
    assert info.match_left == 12
    assert info.match_top == 34
    assert info.capture_left == request.capture_region.left
    assert info.capture_top == request.capture_region.top


def test_space_system_normalization():
    assert SpaceSystem.normalize("stanton") is SpaceSystem.STANTON
    assert SpaceSystem.normalize("Pyro") is SpaceSystem.PYRO
    assert SpaceSystem.normalize("nyx") is SpaceSystem.NYX
    assert SpaceSystem.normalize("unknown") is SpaceSystem.STANTON
