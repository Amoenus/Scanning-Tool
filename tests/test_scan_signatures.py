from typing import Dict

from pathlib import Path

from scanning_tool.deposits.scan_signatures import (
    bootstrap_scan_signature_registry,
    parse_scan_signature_row,
)
from scanning_tool.domain.models import ScanSignature


def test_parse_scan_signature_row_parses_valid_csv_values():
    row: Dict[str, object] = {
        "mineral": "Iron Ore",
        "category": "Metal",
        "base_value": "3",
        "max_multiplier": "7",
    }

    signature = parse_scan_signature_row(row)

    assert signature == ScanSignature(
        name="Iron Ore",
        category="Metal",
        base_value=3,
        max_multiplier=7,
    )


def test_parse_scan_signature_row_rejects_incomplete_rows():
    assert parse_scan_signature_row({"mineral": "", "category": "Metal", "base_value": "3", "max_multiplier": "7"}) is None
    assert parse_scan_signature_row({"mineral": "Iron", "category": "", "base_value": "3", "max_multiplier": "7"}) is None
    assert parse_scan_signature_row({"mineral": "Iron", "category": "Metal", "base_value": "abc", "max_multiplier": "7"}) is None
    assert parse_scan_signature_row({"mineral": "Iron", "category": "Metal", "base_value": "3", "max_multiplier": ""}) is None


def test_bootstrap_scan_signature_registry_reads_csv(tmp_path: Path):
    csv_path = tmp_path / "scan_signatures_summary.csv"
    csv_path.write_text(
        "mineral,category,base_value,max_multiplier\nIRON,Metal,10,5\n"
    )

    registry = bootstrap_scan_signature_registry(csv_path)
    signature = registry.get(10)

    assert signature is not None
    assert signature.name == "IRON"
    assert signature.category == "Metal"
