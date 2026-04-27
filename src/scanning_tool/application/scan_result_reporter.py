"""Scan result reporting helpers for logs and UI status messages."""
from __future__ import annotations


import re

from loguru import logger



from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.capture import ScanResult
class ScanResultMessageFormatter:
    """Builds and formats a canonical scan result message string."""

    MESSAGE_TEMPLATE = (
        "Scan result: ScanResult(label={}, region={}, code_raw={}, raw_text={})"
    )

    @staticmethod
    def format(result: ScanResult) -> str:
        return ScanResultMessageFormatter.MESSAGE_TEMPLATE.format(
            result.label,
            result.region,
            result.code_raw,
            result.raw_text,
        )

    @staticmethod
    def highlight_numbers(text: str) -> str:
        return re.sub(r"(\d+)", r"<yellow>\1</yellow>", text)


class ScanResultReporter:
    """Format and publish scan results for both logs and status callbacks."""

    @staticmethod
    def format(result: ScanResult) -> str:
        return ScanResultMessageFormatter.format(result)

    @staticmethod
    def format_status_message(result: ScanResult) -> str:
        return ScanResultMessageFormatter.highlight_numbers(
            ScanResultMessageFormatter.format(result),
        )

    @staticmethod
    def log(result: ScanResult) -> None:
        logger.info(
            ScanResultMessageFormatter.MESSAGE_TEMPLATE,
            result.label,
            result.region,
            result.code_raw,
            result.raw_text,
        )
