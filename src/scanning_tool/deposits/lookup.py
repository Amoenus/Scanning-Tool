"""Deposit lookup and code extraction from OCR text."""

import re
from typing import Optional, Pattern

from scanning_tool.state.manager import service_state
from scanning_tool.domain.models import (
    CodeExtraction,
    DepositInfo,
    ScanSignature,
    SignatureRegistry,
)
from scanning_tool.deposits.scan_signatures import SCAN_SIGNATURE_REGISTRY


class DepositCodeParser:
    """Parse deposit codes out of OCR text and normalize them."""

    _lookup_deposit_re: Pattern[str] = re.compile(r"(\d+)$")
    _parse_alpha_code_re: Pattern[str] = re.compile(r"([A-Za-z]?-?)([\d,\.]+)")

    def __init__(self, code_re: Pattern[str]) -> None:
        self.code_re = code_re

    def extract_code(self, raw_text: str) -> CodeExtraction:
        """Extract a code and raw match from OCR text."""
        if not raw_text:
            return CodeExtraction(code=None, raw=None)

        match = self.code_re.search(raw_text)
        if not match:
            return CodeExtraction(code=None, raw=raw_text)

        raw = match.group(0).upper()
        return CodeExtraction(code=self._normalize_code(raw), raw=raw)

    def _normalize_code(self, raw: str) -> str:
        raw = raw.replace(",", "").replace(".", "")
        match = self._parse_alpha_code_re.match(raw)
        if match:
            prefix, digits = match.groups()
            return prefix + digits
        return raw

    def extract_numeric_suffix(self, code: str) -> Optional[int]:
        """Return the last numeric segment of a deposit code, if present."""
        match = self._lookup_deposit_re.search(code)
        if not match:
            return None

        try:
            return int(match.group(1))
        except ValueError:
            return None


class DepositLookupService:
    """Lookup deposit metadata from a scan signature registry."""

    def __init__(self, registry: "SignatureRegistry") -> None:
        self._registry = registry

    def lookup(self, code: Optional[str]) -> Optional[DepositInfo]:
        """Return deposit metadata when the code matches a known signature."""
        if not code:
            return None

        num_code = DepositCodeParser._lookup_deposit_re.search(code)
        if num_code is None:
            return None

        numeric_code = self._extract_numeric_suffix(code)
        if numeric_code is None:
            return None

        for base_value, signature in self._registry.get_all().items():
            if numeric_code % base_value == 0:
                return self._build_deposit_info(base_value, signature, numeric_code)

        return None

    @staticmethod
    def _extract_numeric_suffix(code: str) -> Optional[int]:
        match = DepositCodeParser._lookup_deposit_re.search(code)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    @staticmethod
    def _build_deposit_info(
        base_value: int, signature: ScanSignature, numeric_code: int
    ) -> DepositInfo:
        return DepositInfo(
            name=signature.name,
            base_code=base_value,
            deposits=numeric_code // base_value,
            category=signature.category,
            max_multiplier=signature.max_multiplier,
        )


_code_parser = DepositCodeParser(service_state.code_re)


def lookup_deposit(code: Optional[str]) -> Optional[DepositInfo]:
    """Look up a deposit by its numeric code using scraped scan signature data."""
    from scanning_tool.deposits.scan_signatures import get_scan_signature_registry

    return DepositLookupService(get_scan_signature_registry()).lookup(code)


def extract_code_from_text(raw_text: str) -> CodeExtraction:
    """Extract a deposit code from OCR text."""
    return DepositCodeParser(service_state.code_re).extract_code(raw_text)
