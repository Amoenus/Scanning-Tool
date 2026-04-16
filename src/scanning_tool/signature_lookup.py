from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class SignatureMatch:
    """A single matching row from scan_signatures.csv."""
    mineral: str
    category: str
    color: str
    amount: int
    value: int
    pill_text: str
    pill_title: str


def find_signature_matches(signature_value: int, csv_path: str) -> List[SignatureMatch]:
    """Find all rows in scan_signatures.csv where ``value == signature_value``."""
    try:
        df = pd.read_csv(csv_path)
        matches = df[df['value'] == signature_value]
        return [SignatureMatch(**row) for row in matches.to_dict(orient='records')]
    except Exception:
        return []


if __name__ == "__main__":
    csv_file = Path(__file__).parent.parent.parent / "csv" / "scansig" / "scan_signatures.csv"
    value = int(input("Enter signature value: "))
    results = find_signature_matches(value, str(csv_file))
    if results:
        print(f"Matches for value {value}:")
        for r in results:
            print(r)
    else:
        print(f"No matches found for value {value}.")
