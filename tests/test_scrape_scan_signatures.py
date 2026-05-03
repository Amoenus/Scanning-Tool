import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scrape_scan_signatures import ScanSignatureExporter

from scanning_tool.deposits.scan_signature_scraper import (
    ScanSignatureEntry,
    ScanValue,
    load_manual_overrides,
    parse_color_to_category,
)


def test_scan_signature_entry_to_csv_rows():
    entry = ScanSignatureEntry(
        mineral="Quantainium",
        color="rgb(255, 170, 51)",
        values=[
            ScanValue(
                text="Quantainium ×1 = 1,000",
                title="Quantainium ×1 = 1,000",
                amount=1,
                value=1000,
            ),
            ScanValue(
                text="Quantainium ×2 = 2,000",
                title="Quantainium ×2 = 2,000",
                amount=2,
                value=2000,
            ),
        ],
        category="legendary",
    )

    assert entry.to_csv_rows() == [
        {
            "mineral": "Quantainium",
            "category": "legendary",
            "color": "rgb(255, 170, 51)",
            "amount": 1,
            "value": 1000,
            "pill_text": "Quantainium ×1 = 1,000",
            "pill_title": "Quantainium ×1 = 1,000",
        },
        {
            "mineral": "Quantainium",
            "category": "legendary",
            "color": "rgb(255, 170, 51)",
            "amount": 2,
            "value": 2000,
            "pill_text": "Quantainium ×2 = 2,000",
            "pill_title": "Quantainium ×2 = 2,000",
        },
    ]


def test_scan_signature_entry_to_summary_row():
    entry = ScanSignatureEntry(
        mineral="Quantainium",
        color="rgb(255, 170, 51)",
        values=[
            ScanValue(text="x1", title="x1", amount=1, value=1000),
            ScanValue(text="x2", title="x2", amount=2, value=2000),
        ],
        category="legendary",
    )

    assert entry.to_summary_row() == {
        "mineral": "Quantainium",
        "category": "legendary",
        "base_value": 1000,
        "max_multiplier": 2,
    }


def test_parse_color_to_category_returns_raw_color_for_unknown_values():
    assert parse_color_to_category("rgb(1, 1, 1)") == "rgb(1, 1, 1)"


def test_scan_signature_exporter_writes_files(tmp_path: Path):
    entry = ScanSignatureEntry(
        mineral="Quantainium",
        color="rgb(255, 170, 51)",
        values=[
            ScanValue(
                text="Quantainium ×1 = 1,000",
                title="Quantainium ×1 = 1,000",
                amount=1,
                value=1000,
            ),
            ScanValue(
                text="Quantainium ×2 = 2,000",
                title="Quantainium ×2 = 2,000",
                amount=2,
                value=2000,
            ),
        ],
        category="legendary",
    )
    exporter = ScanSignatureExporter(output_dir=tmp_path)

    csv_path = tmp_path / "scan_signatures.csv"
    summary_path = tmp_path / "scan_signatures_summary.csv"
    json_path = tmp_path / "scan_signatures.json"

    exporter.save_csv([entry], csv_path)
    exporter.save_summary_csv([entry], summary_path)
    exporter.save_json([entry], json_path)

    assert csv_path.exists()
    assert summary_path.exists()
    assert json_path.exists()

    csv_text = csv_path.read_text(encoding="utf-8")
    summary_text = summary_path.read_text(encoding="utf-8")
    json_data = json.loads(json_path.read_text(encoding="utf-8"))

    assert "Quantainium" in csv_text
    assert "base_value" in summary_text
    assert isinstance(json_data, list)
    assert json_data[0]["mineral"] == "Quantainium"


def test_load_manual_overrides_returns_empty_for_missing_file(tmp_path: Path) -> None:
    result = load_manual_overrides(tmp_path / "nonexistent.json")
    assert result == []


def test_load_manual_overrides_parses_entries(tmp_path: Path) -> None:
    override_file = tmp_path / "manual_overrides.json"
    override_file.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "mineral": "Tin (Salvage)",
                        "category": "common",
                        "color": "rgb(136, 153, 170)",
                        "amount": 1,
                        "value": 1700,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = load_manual_overrides(override_file)

    assert len(result) == 1
    entry = result[0]
    assert entry.mineral == "Tin (Salvage)"
    assert entry.category == "common"
    assert entry.color == "rgb(136, 153, 170)"
    assert len(entry.values) == 1
    assert entry.values[0].amount == 1
    assert entry.values[0].value == 1700
    assert entry.values[0].text == "1,700"
    assert entry.values[0].title == "Tin (Salvage) \u00d71 = 1,700"
