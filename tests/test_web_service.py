from scanning_tool.config import resource_path
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.models import AlignmentInfo, DepositInfo, ScanResult
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.web.app import WebService


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
    )

    app = web_service.create_app()
    client = app.test_client()
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json["last"]["label"] == "ORE123"
    assert response.json["info"]["name"] == "Ore 123"
    assert response.json["code_raw"] == "ORE123"
    assert response.json["selected_region"] == "STANTON"
