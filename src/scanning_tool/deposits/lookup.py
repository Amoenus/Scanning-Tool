"""Deposit lookup and code extraction from OCR text."""

import re
from typing import Optional

from scanning_tool.core.state_manager import service_state
from scanning_tool.domain.models import CodeExtraction, DepositInfo
from scanning_tool.deposits.scan_signatures import SCAN_SIGNATURES

_LOOKUP_DEPOSIT_RE = re.compile(r"(\d+)$")
_PARSE_ALPHA_CODE_RE = re.compile(r"([A-Za-z]?-?)([\d,\.]+)")


def lookup_deposit(code: Optional[str]) -> Optional[DepositInfo]:
    """Look up a deposit by its numeric code using scraped scan signature data."""
    if not code:
        return None
    try:
        m = _LOOKUP_DEPOSIT_RE.search(code)
        if not m:
            return None
        num_code = int(m.group(1))
        for base_value, sig in SCAN_SIGNATURES.items():
            if num_code % base_value == 0:
                return DepositInfo(
                    name=sig.name,
                    base_code=base_value,
                    deposits=num_code // base_value,
                    category=sig.category,
                    max_multiplier=sig.max_multiplier,
                )
    except Exception:
        pass
    return None


def _parse_alphanumeric_code(raw: str) -> str:
    m = _PARSE_ALPHA_CODE_RE.match(raw)
    if m:
        prefix, digits = m.groups()
        digits = digits.replace(",", "").replace(".", "")
        return prefix + digits
    return raw.replace(",", "").replace(".", "")


def extract_code_from_text(raw_text: str) -> CodeExtraction:
    """Extract a deposit code from OCR text."""
    if not raw_text:
        return CodeExtraction(code=None, raw=None)
    matches = service_state.code_re.findall(raw_text)
    if not matches:
        return CodeExtraction(code=None, raw=raw_text)
    raw = matches[0].upper()
    if any(ch.isdigit() for ch in raw):
        candidate = _parse_alphanumeric_code(raw)
    else:
        candidate = raw
    return CodeExtraction(code=candidate, raw=raw)
