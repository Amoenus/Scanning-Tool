"""Deposit lookup and code extraction from OCR text."""

import re
from dataclasses import dataclass
from typing import Optional, Pattern

from scanning_tool.state.manager import service_state
from scanning_tool.domain.capture import CodeExtraction, DepositInfo
from scanning_tool.domain.scan_signature import ScanSignature, SignatureRegistry


@dataclass(frozen=True)
class DepositSignatureMatch:
    base_value: int
    signature: ScanSignature

    def to_deposit_info(self, numeric_code: int) -> DepositInfo:
        return DepositInfo(
            name=self.signature.name,
            base_code=self.base_value,
            deposits=numeric_code // self.base_value,
            category=self.signature.category,
            max_multiplier=self.signature.max_multiplier,
        )


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


class DepositSignatureMatcher:
    """Encapsulates deposit signature matching and DepositInfo creation."""

    def __init__(self, registry: "SignatureRegistry") -> None:
        self._registry = registry

    def match(self, numeric_code: int) -> Optional[DepositSignatureMatch]:
        for base_value, signature in self._registry.get_all().items():
            if numeric_code % base_value == 0:
                return DepositSignatureMatch(base_value=base_value, signature=signature)
        return None


def _get_default_code_parser() -> DepositCodeParser:
    return DepositCodeParser(service_state.code_re)


class DepositLookupService:
    """Lookup deposit metadata from a scan signature registry."""

    def __init__(
        self,
        registry: "SignatureRegistry",
        parser: Optional[DepositCodeParser] = None,
        matcher: Optional[DepositSignatureMatcher] = None,
    ) -> None:
        self._parser = parser or _get_default_code_parser()
        self._matcher = matcher or DepositSignatureMatcher(registry)

    def lookup(self, code: Optional[str]) -> Optional[DepositInfo]:
        """Return deposit metadata when the code matches a known signature."""
        if not code:
            return None

        numeric_code = self._extract_numeric_code(code)
        if numeric_code is None:
            return None

        signature_match = self._matcher.match(numeric_code)
        if signature_match is None:
            return None

        return signature_match.to_deposit_info(numeric_code)

    def _extract_numeric_code(self, code: str) -> Optional[int]:
        return self._parser.extract_numeric_suffix(code)


_code_parser = DepositCodeParser(service_state.code_re)


def lookup_deposit(code: Optional[str]) -> Optional[DepositInfo]:
    """Look up a deposit by its numeric code using scraped scan signature data."""
    from scanning_tool.deposits.scan_signatures import get_scan_signature_registry

    return DepositLookupService(
        get_scan_signature_registry(), parser=_code_parser
    ).lookup(code)


def extract_code_from_text(raw_text: str) -> CodeExtraction:
    """Extract a deposit code from OCR text."""
    return _code_parser.extract_code(raw_text)
