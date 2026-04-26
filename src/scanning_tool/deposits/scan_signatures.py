"""Load scan signature data from CSV."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional

from loguru import logger
import pandas as pd  # type: ignore[import]

from scanning_tool.domain.dtos import ScanSignatureCSVRowData
from scanning_tool.domain.scan_signature import (
    ScanSignature,
    ScanSignatureCSVRow,
    SignatureRegistry,
)


SCAN_SIG_CSV = (
    Path(__file__).resolve().parents[3]
    / "csv"
    / "scansig"
    / "scan_signatures_summary.csv"
)


def parse_scan_signature_row(
    row: ScanSignatureCSVRowData | Mapping[str, object] | pd.Series | None,
) -> Optional[ScanSignature]:
    if row is None or len(row) == 0:
        return None

    return ScanSignatureCSVRow.from_mapping(row).to_scan_signature()


def load_scan_signatures(path: Path | str) -> SignatureRegistry:
    path = Path(path)
    registry = SignatureRegistry()
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        logger.warning(
            "Scan signature CSV not found",
            path=str(path),
        )
        return registry
    except Exception as exc:
        logger.warning(
            "Failed to load scan signature CSV",
            path=str(path),
            error=exc,
        )
        return registry

    for _, row in df.iterrows():
        signature = parse_scan_signature_row(row)
        if signature is not None:
            registry.add(signature)
        else:
            logger.warning(
                "Bad scan signature row",
                row=str(row),
            )
    return registry


_scan_signature_registry_loaded = False


def bootstrap_scan_signature_registry(
    path: Path | str = SCAN_SIG_CSV,
) -> SignatureRegistry:
    global _scan_signature_registry_loaded

    if isinstance(path, str):
        path = Path(path)

    loaded_registry = load_scan_signatures(path)
    SCAN_SIGNATURE_REGISTRY.replace_signatures(loaded_registry.get_all())
    _scan_signature_registry_loaded = True
    return SCAN_SIGNATURE_REGISTRY


def get_scan_signature_registry() -> SignatureRegistry:
    global _scan_signature_registry_loaded

    if not _scan_signature_registry_loaded:
        bootstrap_scan_signature_registry()
    return SCAN_SIGNATURE_REGISTRY


SCAN_SIGNATURE_REGISTRY: SignatureRegistry = SignatureRegistry()
