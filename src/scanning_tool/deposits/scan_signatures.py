"""Load scan signature data from CSV."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from loguru import logger
import pandas as pd  # type: ignore[import]

from scanning_tool.domain.dtos import ScanSignatureCSVRowData
from scanning_tool.domain.models import ScanSignature, SignatureRegistry


@dataclass(frozen=True)
class ScanSignatureRow:
    mineral: Optional[str] = None
    category: Optional[str] = None
    base_value: Optional[int | float | str] = None
    max_multiplier: Optional[int | float | str] = None

    @classmethod
    def from_mapping(
        cls, row: ScanSignatureCSVRowData | pd.Series | None
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


def _to_int(value: object | None) -> Optional[int]:
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


def _to_str(value: object | None) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def parse_scan_signature_row(row: ScanSignatureCSVRowData | pd.Series | None) -> Optional[ScanSignature]:
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
