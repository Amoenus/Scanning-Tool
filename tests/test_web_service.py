import logging

from scanning_tool.config import resource_path
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.common import OreTableEntry, SpaceSystem
from scanning_tool.domain.models import AlignmentInfo, DepositInfo, ScanResult
from scanning_tool.logging_setup import InterceptHandler
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.web.app import DefaultStatusResponseBuilder, WebService


def test_web_service_status_exposes_latest_scan_result():
    config = ConfigData()
    scan_state = ScanState()
    scan_state.last_alignment_info = AlignmentInfo(enabled=True, matched=False)
    scan_state.last_result = ScanResult(
        label="ORE123",
        region=config.capture_region,
        info=DepositInfo(key="ore123", name="Ore 123", category="rock deposits"),
        code_raw="ORE123",
        raw_text="raw ocr text",
    )
    service_state = ServiceState()
    web_service = WebService(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        template_folder=resource_path("templates"),
        status_response_builder=DefaultStatusResponseBuilder(),
    )

    app = web_service.create_app()
    client = app.test_client()
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json["last"]["label"] == "ORE123"
    assert response.json["info"]["name"] == "Ore 123"
    assert response.json["code_raw"] == "ORE123"
    assert response.json["selected_region"] == "STANTON"
    assert response.json["status"] == "ok"
    assert response.json["updated_at"] is not None
    assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"


def test_web_service_health_endpoint_returns_ok():
    config = ConfigData()
    scan_state = ScanState()
    service_state = ServiceState()
    web_service = WebService(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        template_folder=resource_path("templates"),
        status_response_builder=DefaultStatusResponseBuilder(),
    )

    app = web_service.create_app()
    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_status_response_builder_includes_supported_deposit_table():
    builder = DefaultStatusResponseBuilder()
    info = DepositInfo(key="ore123", name="Ore 123", category="rock deposits")
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
                color="#fff",
            ),
        ],
    }

    table = builder._lookup_deposit_table(info, SpaceSystem.STANTON, service_state)

    assert table is not None
    assert table[0].name == "Ore 123"


def test_flask_app_routes_logs_through_loguru_intercept_handler():
    config = ConfigData()
    scan_state = ScanState()
    service_state = ServiceState()
    web_service = WebService(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        template_folder=resource_path("templates"),
        status_response_builder=DefaultStatusResponseBuilder(),
    )

    app = web_service.create_app()

    assert any(isinstance(handler, InterceptHandler) for handler in app.logger.handlers)
    assert app.logger.propagate is False
    assert any(
        isinstance(handler, InterceptHandler)
        for handler in logging.getLogger("werkzeug").handlers
    )
    assert any(
        isinstance(handler, InterceptHandler)
        for handler in logging.getLogger("flask").handlers
    )


def test_setup_logging_intercepts_flask_and_werkzeug_loggers():
    from scanning_tool.logging_setup import setup_logging

    setup_logging()

    assert any(
        isinstance(handler, InterceptHandler)
        for handler in logging.getLogger("werkzeug").handlers
    )
    assert any(
        isinstance(handler, InterceptHandler)
        for handler in logging.getLogger("flask").handlers
    )
    assert any(
        isinstance(handler, InterceptHandler)
        for handler in logging.getLogger("flask.app").handlers
    )
