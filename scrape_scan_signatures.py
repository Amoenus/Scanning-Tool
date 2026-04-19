"""
Scrape Scan Signature Identifier data from https://scmdb.net/?page=mine
Extracts mineral name, scan values, rarity/color, and category from the overlay.
Outputs JSON and CSV formats.
"""

import asyncio
import json
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

from playwright.async_api import Page, async_playwright

OUTPUT_DIR = Path("csv/scansig")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://scmdb.net/?page=mine"


SCRAPE_SIGNATURES_SCRIPT = """() => {
            const rows = Array.from(document.querySelectorAll('.sigchart-row'));
            return rows.map(row => {
                const labelDiv = row.querySelector('.sigchart-label');
                const color = labelDiv ? labelDiv.style.color : null;
                const mineral = labelDiv ? labelDiv.textContent.trim() : null;
                const pills = Array.from(row.querySelectorAll('.sigchart-pill'));
                const values = pills.map(pill => {
                    const m = pill.title.match(/(.+) ×(\d+) = ([\d,]+)/);
                    return {
                        text: pill.textContent.trim(),
                        title: pill.title,
                        amount: m ? parseInt(m[2]) : null,
                        value: m ? parseInt(m[3].replace(/,/g, '')) : null,
                    };
                });
                return {
                    mineral,
                    color,
                    values,
                };
            });
        }"""


class RawScanValue(TypedDict, total=False):
    text: Optional[str]
    title: Optional[str]
    amount: Optional[int]
    value: Optional[int]


class RawScanSignatureEntry(TypedDict, total=False):
    mineral: Optional[str]
    color: Optional[str]
    values: List[RawScanValue]


CsvRow = Dict[str, Optional[str | int]]


@dataclass(frozen=True)
class ScanValue:
    text: Optional[str]
    title: Optional[str]
    amount: Optional[int]
    value: Optional[int]

    def to_csv_row(
        self,
        mineral: Optional[str],
        category: str,
        color: Optional[str],
    ) -> CsvRow:
        return {
            "mineral": mineral,
            "category": category,
            "color": color,
            "amount": self.amount,
            "value": self.value,
            "pill_text": self.text,
            "pill_title": self.title,
        }


@dataclass(frozen=True)
class ScanSignatureEntry:
    mineral: Optional[str]
    color: Optional[str]
    values: List[ScanValue]
    category: str

    def to_csv_rows(self) -> List[CsvRow]:
        return [
            value.to_csv_row(mineral=self.mineral, category=self.category, color=self.color)
            for value in self.values
        ]

    def to_summary_row(self) -> CsvRow:
        return {
            "mineral": self.mineral,
            "category": self.category,
            "base_value": self._find_base_value(),
            "max_multiplier": self._find_max_multiplier(),
        }

    def _find_base_value(self) -> Optional[int]:
        for value in self.values:
            if value.amount == 1:
                return value.value
        return self.values[0].value if self.values else None

    def _find_max_multiplier(self) -> Optional[int]:
        max_multiplier: Optional[int] = None
        for value in self.values:
            if value.amount is not None and (
                max_multiplier is None or value.amount > max_multiplier
            ):
                max_multiplier = value.amount
        return max_multiplier


def parse_color_to_category(color: str) -> str:
    """Map RGB color to rarity/category string."""
    color_map = {
        "rgb(255, 170, 51)": "legendary",
        "rgb(204, 102, 255)": "epic",
        "rgb(51, 153, 255)": "rare",
        "rgb(51, 204, 170)": "uncommon",
        "rgb(136, 153, 170)": "common",
        "rgb(102, 221, 170)": "ROC Mineables",
        "rgb(119, 187, 221)": "FPS Mineables",
        "rgb(170, 153, 119)": "Salvage",
    }
    return color_map.get(color, color)


def _as_optional_str(value: object | None) -> Optional[str]:
    return value if isinstance(value, str) else None


def _create_scan_value(raw_value: RawScanValue) -> ScanValue:
    return ScanValue(
        text=_as_optional_str(raw_value.get("text")),
        title=_as_optional_str(raw_value.get("title")),
        amount=raw_value.get("amount"),
        value=raw_value.get("value"),
    )


def _create_scan_signature_entry(raw_entry: RawScanSignatureEntry) -> ScanSignatureEntry:
    raw_values = raw_entry.get("values") or []
    values = [_create_scan_value(raw_value) for raw_value in raw_values]

    color = _as_optional_str(raw_entry.get("color"))
    return ScanSignatureEntry(
        mineral=_as_optional_str(raw_entry.get("mineral")),
        color=color,
        values=values,
        category=parse_color_to_category(color or ""),
    )


async def _evaluate_scan_signature_overlay(page: Page) -> List[RawScanSignatureEntry]:
    await page.click('button[title^="Scan Signature Identifier"]')
    await page.wait_for_selector(".sigchart-overlay", timeout=10000)
    return await page.evaluate(SCRAPE_SIGNATURES_SCRIPT)


def _build_scan_signature_entries(raw_data: List[RawScanSignatureEntry]) -> List[ScanSignatureEntry]:
    return [_create_scan_signature_entry(raw_entry) for raw_entry in raw_data]


async def scrape_scan_signatures() -> List[ScanSignatureEntry]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TARGET_URL, wait_until="networkidle")

        raw_data = await _evaluate_scan_signature_overlay(page)
        entries = _build_scan_signature_entries(raw_data)

        await browser.close()
        return entries


SAVE_CSV_FIELDNAMES = [
    "mineral",
    "category",
    "color",
    "amount",
    "value",
    "pill_text",
    "pill_title",
]

SUMMARY_CSV_FIELDNAMES = ["mineral", "category", "base_value", "max_multiplier"]


def save_json(data: List[ScanSignatureEntry], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(entry) for entry in data], f, indent=2, ensure_ascii=False)


def _write_csv(path: Path, rows: List[CsvRow], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_csv(data: List[ScanSignatureEntry], path: Path) -> None:
    rows: List[CsvRow] = []
    for entry in data:
        rows.extend(entry.to_csv_rows())

    _write_csv(path, rows, SAVE_CSV_FIELDNAMES)


def save_summary_csv(data: List[ScanSignatureEntry], path: Path) -> None:
    rows: List[CsvRow] = []
    for entry in data:
        rows.append(entry.to_summary_row())

    _write_csv(path, rows, SUMMARY_CSV_FIELDNAMES)


def main() -> None:
    data = asyncio.run(scrape_scan_signatures())
    save_json(data, OUTPUT_DIR / "scan_signatures.json")
    save_csv(data, OUTPUT_DIR / "scan_signatures.csv")
    save_summary_csv(data, OUTPUT_DIR / "scan_signatures_summary.csv")
    print(
        f"Saved {len(data)} minerals to {OUTPUT_DIR}/scan_signatures.json, .csv, and scan_signatures_summary.csv"
    )


if __name__ == "__main__":
    main()
