from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from scanning_tool.domain.alignment import CaptureRegion


@dataclass
class DepositInfo:
    """Structured metadata for a detected deposit or scan signature."""

    key: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    id: Optional[str | int] = None
    base_code: Optional[int] = None
    deposits: Optional[int] = None
    max_multiplier: Optional[int] = None


@dataclass
class ScanResult:
    """A single scan result from OCR with resolved deposit metadata."""

    label: str
    region: CaptureRegion
    info: Optional[DepositInfo] = None
    code_raw: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class CodeExtraction:
    """Output of parsing a deposit code from OCR text."""

    code: Optional[str]
    raw: Optional[str]
