from __future__ import annotations

from dataclasses import dataclass

from scanning_tool.domain.alignment import CaptureRegion


@dataclass
class DepositInfo:
    """Structured metadata for a detected deposit or scan signature."""

    key: str | None = None
    name: str | None = None
    category: str | None = None
    type: str | None = None
    id: str | int | None = None
    base_code: int | None = None
    deposits: int | None = None
    max_multiplier: int | None = None


@dataclass
class ScanResult:
    """A single scan result from OCR with resolved deposit metadata."""

    label: str
    region: CaptureRegion
    info: DepositInfo | None = None
    code_raw: str | None = None
    raw_text: str | None = None


@dataclass
class CodeExtraction:
    """Output of parsing a deposit code from OCR text."""

    code: str | None
    raw: str | None
