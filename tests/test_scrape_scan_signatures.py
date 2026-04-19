from scrape_scan_signatures import ScanSignatureEntry, ScanValue, parse_color_to_category


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
