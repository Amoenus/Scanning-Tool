"""Load scan signature data from CSV."""

from loguru import logger
from pathlib import Path
from typing import Dict

import pandas as pd

from scanning_tool.domain.models import ScanSignature, SignatureRegistry

SCAN_SIG_CSV = Path(__file__).parent.parent.parent.parent / "csv" / "scansig" / "scan_signatures_summary.csv"


def _load_scan_signatures(path: Path) -> SignatureRegistry:
    registry = SignatureRegistry()
    if not path.exists():
        logger.warning(f"Scan signature CSV not found: {path}")
        return registry
    try:
        df = pd.read_csv(path)
    except Exception as e:
        logger.warning(f"Failed to load scan signature CSV: {e}")
        return registry

    for _, row in df.iterrows():
        try:
            base_value = int(row["base_value"])
            sig = ScanSignature(
                name=row["mineral"],
                category=row["category"],
                base_value=base_value,
                max_multiplier=int(row["max_multiplier"]),
            )
            registry.add(sig)
        except Exception as e:
            logger.warning(f"Bad scan signature row: {row} ({e})")
    return registry


# Apply the class method
SignatureRegistry.load_from_csv = classmethod(lambda cls, path: _load_scan_signatures(Path(path)))

SCAN_SIGNATURE_REGISTRY: SignatureRegistry = _load_scan_signatures(SCAN_SIG_CSV)
