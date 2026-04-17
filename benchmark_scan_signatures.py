import timeit
import pandas as pd
from typing import Dict
from pathlib import Path
from src.scanning_tool.domain.models import ScanSignature

csv_path = Path("csv/scansig/scan_signatures_summary.csv")
df = pd.read_csv(csv_path)

def load_with_iterrows() -> Dict[int, ScanSignature]:
    signatures: Dict[int, ScanSignature] = {}
    for _, row in df.iterrows():
        try:
            base_value = int(row["base_value"])
            signatures[base_value] = ScanSignature(
                name=row["mineral"],
                category=row["category"],
                base_value=base_value,
                max_multiplier=int(row["max_multiplier"]),
            )
        except Exception as e:
            pass
    return signatures

def load_with_itertuples() -> Dict[int, ScanSignature]:
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
            pass
    return signatures

if __name__ == "__main__":
    n = 10000
    t_iterrows = timeit.timeit("load_with_iterrows()", globals=globals(), number=n)
    t_itertuples = timeit.timeit("load_with_itertuples()", globals=globals(), number=n)

    print(f"iterrows: {t_iterrows:.6f} s")
    print(f"itertuples: {t_itertuples:.6f} s")
    print(f"Improvement: {t_iterrows / t_itertuples:.2f}x")
