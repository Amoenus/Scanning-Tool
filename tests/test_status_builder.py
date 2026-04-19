from __future__ import annotations

from scanning_tool.config.service import ConfigData
from scanning_tool.domain.alignment import AlignmentInfo
from scanning_tool.domain.common import OreTableEntry, SpaceSystem
from scanning_tool.domain.capture import DepositInfo, ScanResult
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.web.schemas import StatusResponse
from scanning_tool.web.status_builder import DefaultStatusResponseBuilder, DepositTableResolver


def test_deposit_table_resolver_uses_name_when_key_is_missing() -> None:
    resolver = DepositTableResolver()
    info = DepositInfo(key=None, name="Ore 123", category="rock deposits")
    service_state = ServiceState()
    service_state.rocks.deposit_tables[SpaceSystem.STANTON] = {
        "ORE 123": [
            OreTableEntry(
                name="Ore 123",
                prob="100%",
                min="0%",
                max="100%",
                med="50%",
                tier="HIGH",
                color="#ffffff",
            )
        ]
    }

    table = resolver.resolve(info, SpaceSystem.STANTON, service_state)

    assert table is not None
    assert table[0].name == "Ore 123"


def test_deposit_table_resolver_returns_none_for_unsupported_category() -> None:
    resolver = DepositTableResolver()
    info = DepositInfo(key="ore123", name="Ore 123", category="ice")
    service_state = ServiceState()
    service_state.rocks.deposit_tables[SpaceSystem.STANTON] = {
        "ORE123": [
            OreTableEntry(
                name="Ore 123",
                prob="100%",
                min="0%",
                max="100%",
                med="50%",
                tier="HIGH",
                color="#ffffff",
            )
        ]
    }

    table = resolver.resolve(info, SpaceSystem.STANTON, service_state)

    assert table is None


def test_deposit_table_resolver_returns_none_when_table_is_missing() -> None:
    resolver = DepositTableResolver()
    info = DepositInfo(key="ore123", name="Ore 123", category="rock deposits")
    service_state = ServiceState()

    table = resolver.resolve(info, SpaceSystem.STANTON, service_state)

    assert table is None


def test_default_status_response_builder_returns_empty_status_when_no_scan_exists() -> None:
    builder = DefaultStatusResponseBuilder()
    config = ConfigData()
    scan_state = ScanState()
    service_state = ServiceState()

    response = builder.build_status_response(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        selected_region=SpaceSystem.STANTON,
    )

    assert response.last is None
    assert response.code is None
    assert response.code_raw is None
    assert response.raw_text is None
    assert response.table is None
    assert response.selected_region == SpaceSystem.STANTON


def test_status_response_to_dict_serializes_nested_objects() -> None:
    config = ConfigData()
    info = DepositInfo(
        key="ore123",
        name="Ore 123",
        category="rock deposits",
        type="rock",
        id=123,
        base_code=5,
        deposits=1,
        max_multiplier=2,
    )
    scan_result = ScanResult(
        label="ORE123",
        region=config.capture_region,
        info=info,
        code_raw="ORE123",
        raw_text="raw text",
    )
    alignment = AlignmentInfo(
        enabled=True,
        matched=True,
        template="template.png",
        score=0.9,
        match_left=1,
        match_top=2,
        capture_left=3,
        capture_top=4,
    )
    table_entry = OreTableEntry(
        name="Ore 123",
        prob="90%",
        min="10%",
        max="90%",
        med="50%",
        tier="HIGH",
        color="#ffffff",
    )

    status = StatusResponse(
        region=config.capture_region,
        label_color=config.overlay_config.label_color,
        last=scan_result,
        alignment=alignment,
        selected_region=SpaceSystem.STANTON,
        info=info,
        code="ORE123",
        code_raw="ORE123",
        raw_text="raw text",
        table=[table_entry],
    )

    serialized = status.to_dict()

    assert serialized["selected_region"] == SpaceSystem.STANTON.value
    assert serialized["last"]["label"] == "ORE123"
    assert serialized["info"]["category"] == "rock deposits"
    assert serialized["alignment"]["template"] == "template.png"
    assert serialized["table"][0]["tier"] == "HIGH"
