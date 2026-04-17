"""Load scan signature data from CSV."""

from loguru import logger
from pathlib import Path
from typing import Dict

import pandas as pd

from scanning_tool.domain.models import ScanSignature

SCAN_SIG_CSV = Path(__file__).parent.parent.parent.parent / "csv" / "scansig" / "scan_signatures_summary.csv"


def _load_scan_signatures() -> Dict[int, ScanSignature]:
    if not SCAN_SIG_CSV.exists():
        logger.warning(f"Scan signature CSV not found: {SCAN_SIG_CSV}")
        return {}
    try:
        df = pd.read_csv(SCAN_SIG_CSV)
    except Exception as e:
        logger.warning(f"Failed to load scan signature CSV: {e}")
        return {}

    signatures: Dict[int, ScanSignature] = {}
    for row in df.itertuples(index=False):
        try:
            base_value = int(row.base_value)
            signatures[base_value] = ScanSignature(
                name=row.mineral,
                category=row.category,
                base_value=base_value,
                max_multiplier=int(row.max_multiplier),
            )
        except Exception as e:
            logger.warning(f"Bad scan signature row: {row} ({e})")
    return signatures


SCAN_SIGNATURES: Dict[int, ScanSignature] = _load_scan_signatures()
