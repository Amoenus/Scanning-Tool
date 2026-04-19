from unittest.mock import patch

from scanning_tool.application.scan_result_reporter import ScanResultReporter
from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.domain.capture import DepositInfo, ScanResult


def test_format_includes_scan_result_values():
    result = ScanResult(
        label="ORE123",
        region=CaptureRegion(left=1, top=2, width=3, height=4),
        info=DepositInfo(key="ore123", name="Ore 123", category="rock deposits"),
        code_raw="123",
        raw_text="Detected code 123",
    )

    formatted = ScanResultReporter.format(result)

    assert "ScanResult(label=ORE123" in formatted
    assert "code_raw=123" in formatted
    assert "raw_text=Detected code 123" in formatted


def test_format_status_message_highlights_numeric_values():
    result = ScanResult(
        label="ORE123",
        region=CaptureRegion(left=0, top=0, width=1, height=1),
        info=DepositInfo(key="ore123", name="Ore 123", category="rock deposits"),
        code_raw="123",
        raw_text="123",
    )

    formatted_status = ScanResultReporter.format_status_message(result)

    assert "<yellow>123</yellow>" in formatted_status
    assert formatted_status.count("<yellow>123</yellow>") >= 1


@patch("scanning_tool.application.scan_result_reporter.logger")
def test_log_calls_logger_info(mock_logger):
    result = ScanResult(
        label="ORE123",
        region=CaptureRegion(left=0, top=0, width=1, height=1),
        info=DepositInfo(key="ore123", name="Ore 123", category="rock deposits"),
        code_raw="123",
        raw_text="123",
    )

    ScanResultReporter.log(result)

    mock_logger.info.assert_called_once_with(
        "Scan result: ScanResult(label={}, region={}, code_raw={}, raw_text={})",
        result.label,
        result.region,
        result.code_raw,
        result.raw_text,
    )
