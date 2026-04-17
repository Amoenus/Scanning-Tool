import timeit
import pandas as pd
from typing import Any, Dict, Optional
from pathlib import Path
from src.scanning_tool.domain.models import ScanSignature

csv_path = Path("csv/scansig/scan_signatures_summary.csv")
df = pd.read_csv(csv_path)


def _parse_int(value: Any) -> Optional[int]:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _normalize_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _build_scan_signature(
    name: Any,
    category: Any,
    base_value: Any,
    max_multiplier: Any,
) -> Optional[ScanSignature]:
    parsed_base_value = _parse_int(base_value)
    parsed_max_multiplier = _parse_int(max_multiplier)
    if parsed_base_value is None or parsed_max_multiplier is None:
        return None

    parsed_name = _normalize_str(name)
    parsed_category = _normalize_str(category)
    if not parsed_name or not parsed_category:
        return None

    return ScanSignature(
        name=parsed_name,
        category=parsed_category,
        base_value=parsed_base_value,
        max_multiplier=parsed_max_multiplier,
    )


def load_with_iterrows() -> Dict[int, ScanSignature]:
    signatures: Dict[int, ScanSignature] = {}
    for _, row in df.iterrows():
        signature = _build_scan_signature(
            name=row["mineral"],
            category=row["category"],
            base_value=row["base_value"],
            max_multiplier=row["max_multiplier"],
        )
        if signature is not None:
            signatures[signature.base_value] = signature
    return signatures


def load_with_itertuples() -> Dict[int, ScanSignature]:
    signatures: Dict[int, ScanSignature] = {}
    for row in df.itertuples(index=False):
        signature = _build_scan_signature(
            name=row.mineral,
            category=row.category,
            base_value=row.base_value,
            max_multiplier=row.max_multiplier,
        )
        if signature is not None:
            signatures[signature.base_value] = signature
    return signatures


if __name__ == "__main__":
    n = 10000
    t_iterrows = timeit.timeit("load_with_iterrows()", globals=globals(), number=n)
    t_itertuples = timeit.timeit("load_with_itertuples()", globals=globals(), number=n)

    print(f"iterrows: {t_iterrows:.6f} s")
    print(f"itertuples: {t_itertuples:.6f} s")
    print(f"Improvement: {t_iterrows / t_itertuples:.2f}x")
