from typing import Dict

from scanning_tool.deposits.scan_signatures import parse_scan_signature_row
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
