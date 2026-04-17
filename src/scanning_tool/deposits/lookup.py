"""Deposit lookup and code extraction from OCR text."""

import re
from typing import Optional

from scanning_tool.core.state_manager import service_state
from scanning_tool.domain.models import CodeExtraction, DepositInfo, ScanSignature
from scanning_tool.deposits.scan_signatures import SCAN_SIGNATURE_REGISTRY

_LOOKUP_DEPOSIT_RE = re.compile(r"(\d+)$")
_PARSE_ALPHA_CODE_RE = re.compile(r"([A-Za-z]?-?)([\d,\.]+)")


def _extract_numeric_suffix(code: str) -> Optional[int]:
    """Return the last numeric segment of a deposit code, if present."""
    m = _LOOKUP_DEPOSIT_RE.search(code)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _build_deposit_info(base_value: int, sig: ScanSignature, num_code: int) -> DepositInfo:
    return DepositInfo(
        name=sig.name,
        base_code=base_value,
        deposits=num_code // base_value,
        category=sig.category,
        max_multiplier=sig.max_multiplier,
    )


def lookup_deposit(code: Optional[str]) -> Optional[DepositInfo]:
    """Look up a deposit by its numeric code using scraped scan signature data."""
    if not code:
        return None

    num_code = _extract_numeric_suffix(code)
    if num_code is None:
        return None

    for base_value, sig in SCAN_SIGNATURE_REGISTRY.get_all().items():
        if num_code % base_value == 0:
            return _build_deposit_info(base_value, sig, num_code)

    return None


def _normalize_code(raw: str) -> str:
    raw = raw.replace(",", "").replace(".", "")
    m = _PARSE_ALPHA_CODE_RE.match(raw)
    if m:
        prefix, digits = m.groups()
        return prefix + digits
    return raw


def extract_code_from_text(raw_text: str) -> CodeExtraction:
    """Extract a deposit code from OCR text."""
    if not raw_text:
        return CodeExtraction(code=None, raw=None)

    match = service_state.code_re.search(raw_text)
    if not match:
        return CodeExtraction(code=None, raw=raw_text)

    raw = match.group(0).upper()
    return CodeExtraction(code=_normalize_code(raw), raw=raw)
