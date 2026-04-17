"""Load scan signature data from CSV."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger
import pandas as pd  # type: ignore[import]

from scanning_tool.domain.dtos import ScanSignatureCSVRowData
from scanning_tool.domain.models import (
    ScanSignature,
    ScanSignatureCSVRow,
    SignatureRegistry,
)


SCAN_SIG_CSV = (
    Path(__file__).parent.parent.parent.parent
    / "csv"
    / "scansig"
    / "scan_signatures_summary.csv"
)


def parse_scan_signature_row(row: ScanSignatureCSVRowData | pd.Series | None) -> Optional[ScanSignature]:
    if row is None or len(row) == 0:
        return None

    return ScanSignatureCSVRow.from_mapping(row).to_scan_signature()


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
