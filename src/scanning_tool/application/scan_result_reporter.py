"""Scan result reporting helpers for logs and UI status messages."""

import re

from loguru import logger

from scanning_tool.domain.capture import ScanResult


class ScanResultReporter:
    """Format and publish scan results for both logs and status callbacks."""

    @staticmethod
    def format(result: ScanResult) -> str:
        return (
            f"Scan result: ScanResult(label={result.label}, region={result.region}, "
            f"code_raw={result.code_raw}, raw_text={result.raw_text})"
        )

    @staticmethod
    def format_status_message(result: ScanResult) -> str:
        return ScanResultReporter._highlight_numbers(ScanResultReporter.format(result))

    @staticmethod
    def log(result: ScanResult) -> None:
        logger.info(
            "Scan result: ScanResult(label={}, region={}, code_raw={}, raw_text={})",
            result.label,
            result.region,
            result.code_raw,
            result.raw_text,
        )

    @staticmethod
    def _highlight_numbers(text: str) -> str:
        return re.sub(r"(\d+)", r"<yellow>\1</yellow>", text)
