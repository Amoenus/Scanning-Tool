"""Load scan signature data from CSV."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, TypedDict

from loguru import logger
import pandas as pd  # type: ignore[import]

from scanning_tool.domain.models import ScanSignature, SignatureRegistry


class ScanSignatureCSVRow(TypedDict, total=False):
    mineral: str
    category: str
    base_value: int | float | str
    max_multiplier: int | float | str


@dataclass(frozen=True)
class ScanSignatureRow:
    mineral: Any = None
    category: Any = None
    base_value: Any = None
    max_multiplier: Any = None

    @classmethod
    def from_mapping(
        cls, row: Mapping[str, Any] | pd.Series
    ) -> "ScanSignatureRow":
        if row is None:
            return cls()

        return cls(
            mineral=row.get("mineral"),
            category=row.get("category"),
            base_value=row.get("base_value"),
            max_multiplier=row.get("max_multiplier"),
        )

    def to_scan_signature(self) -> Optional[ScanSignature]:
        name = _to_str(self.mineral)
        category = _to_str(self.category)
        base_value = _to_int(self.base_value)
        max_multiplier = _to_int(self.max_multiplier)

        if not name or not category or base_value is None or max_multiplier is None:
            return None

        return ScanSignature(
            name=name,
            category=category,
            base_value=base_value,
            max_multiplier=max_multiplier,
        )


SCAN_SIG_CSV = (
    Path(__file__).parent.parent.parent.parent
    / "csv"
    / "scansig"
    / "scan_signatures_summary.csv"
)


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value != value:  # NaN check
            return None
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    return None


def _to_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def parse_scan_signature_row(row: Mapping[str, Any] | pd.Series) -> Optional[ScanSignature]:
    if row is None or len(row) == 0:
        return None

    return ScanSignatureRow.from_mapping(row).to_scan_signature()


def _load_scan_signatures(path: Path) -> SignatureRegistry:
    registry = SignatureRegistry()
    if not path.exists():
        logger.warning(f"Scan signature CSV not found: {path}")
        return registry
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        logger.warning(f"Failed to load scan signature CSV: {exc}")
        return registry

    for _, row in df.iterrows():
        signature = parse_scan_signature_row(row)
        if signature is not None:
            registry.add(signature)
        else:
            logger.warning(f"Bad scan signature row: {row}")
    return registry


SCAN_SIGNATURE_REGISTRY: SignatureRegistry = _load_scan_signatures(SCAN_SIG_CSV)
