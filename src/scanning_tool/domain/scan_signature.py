"""Domain models for scan signature CSV parsing and registry management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Optional, cast

from scanning_tool.domain.dtos import ScanSignatureCSVRowData
from scanning_tool.domain.parsers import parse_int, parse_str

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class ScanSignature:
    """An entry in SCAN_SIGNATURES, keyed by base_value."""

    name: str
    category: str
    base_value: int
    max_multiplier: int


@dataclass(frozen=True)
class ScanSignatureCSVRow:
    """Typed representation of one row from the scan signatures CSV."""

    mineral: Optional[str] = None
    category: Optional[str] = None
    base_value: Optional[int | float | str] = None
    max_multiplier: Optional[int | float | str] = None

    @classmethod
    def from_mapping(
        cls, row: ScanSignatureCSVRowData | Mapping[str, object] | "pd.Series" | None
    ) -> "ScanSignatureCSVRow":
        if row is None:
            return cls()

        return cls(
            mineral=cast(Optional[str], row.get("mineral")),
            category=cast(Optional[str], row.get("category")),
            base_value=cast(Optional[int | float | str], row.get("base_value")),
            max_multiplier=cast(Optional[int | float | str], row.get("max_multiplier")),
        )

    @staticmethod
    def _to_int(value: object | None) -> Optional[int]:
        return parse_int(value)

    @staticmethod
    def _to_str(value: object | None) -> Optional[str]:
        return parse_str(value)

    def to_scan_signature(self) -> Optional[ScanSignature]:
        name = self._to_str(self.mineral)
        category = self._to_str(self.category)
        base_value = self._to_int(self.base_value)
        max_multiplier = self._to_int(self.max_multiplier)

        if not name or not category or base_value is None or max_multiplier is None:
            return None

        return ScanSignature(
            name=name,
            category=category,
            base_value=base_value,
            max_multiplier=max_multiplier,
        )


class SignatureRegistry:
    """Domain service to manage a registry of ScanSignatures."""

    def __init__(self, signatures: Optional[dict[int, ScanSignature]] = None) -> None:
        self._signatures = signatures or {}

    def add(self, signature: ScanSignature) -> None:
        self._signatures[signature.base_value] = signature

    def get(self, base_value: int) -> Optional[ScanSignature]:
        return self._signatures.get(base_value)

    def get_all(self) -> dict[int, ScanSignature]:
        return self._signatures.copy()

    @classmethod
    def load_from_csv(cls, path: str | Path) -> "SignatureRegistry":
        from pathlib import Path

        from scanning_tool.deposits.scan_signatures import load_scan_signatures

        return load_scan_signatures(Path(path))
