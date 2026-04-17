import timeit
import pandas as pd
from pathlib import Path
from typing import Dict

from scanning_tool.deposits.scan_signatures import parse_scan_signature_row
from scanning_tool.domain.models import ScanSignature

csv_path = Path("csv/scansig/scan_signatures_summary.csv")
df = pd.read_csv(csv_path)


def load_with_iterrows() -> Dict[int, ScanSignature]:
    signatures: Dict[int, ScanSignature] = {}
    for _, row in df.iterrows():
        signature = parse_scan_signature_row(row)
        if signature is not None:
            signatures[signature.base_value] = signature
    return signatures


def load_with_itertuples() -> Dict[int, ScanSignature]:
    signatures: Dict[int, ScanSignature] = {}
    for row in df.itertuples(index=False):
        signature = parse_scan_signature_row(
            {
                "mineral": row.mineral,
                "category": row.category,
                "base_value": row.base_value,
                "max_multiplier": row.max_multiplier,
            }
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
