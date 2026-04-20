"""
Scrape Scan Signature Identifier data from https://scmdb.net/?page=mine
Extracts mineral name, scan values, rarity/color, and category from the overlay.
Outputs JSON and CSV formats.
"""

from __future__ import annotations

import asyncio
import json
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional
import sys

from playwright.async_api import Page, async_playwright

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scanning_tool.deposits.scan_signature_scraper import (
    CsvRow,
    RawScanValue,
    RawScanSignatureEntry,
    ScanSignatureEntry,
    ScanSignatureEntryFactory,
    ScanSignatureSummary,
    ScanValue,
    parse_color_to_category,
)

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




async def _evaluate_scan_signature_overlay(page: Page) -> List[RawScanSignatureEntry]:
    await page.click('button[title^="Scan Signature Identifier"]')
    await page.wait_for_selector(".sigchart-overlay", timeout=10000)
    return await page.evaluate(SCRAPE_SIGNATURES_SCRIPT)


def _build_scan_signature_entries(raw_data: List[RawScanSignatureEntry]) -> List[ScanSignatureEntry]:
    return [ScanSignatureEntryFactory.from_raw_entry(raw_entry) for raw_entry in raw_data]


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


class ScanSignatureExporter:
    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        self.output_dir = output_dir

    def save_json(self, data: List[ScanSignatureEntry], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(entry) for entry in data], f, indent=2, ensure_ascii=False)

    def _write_csv(self, path: Path, rows: List[CsvRow], fieldnames: list[str]) -> None:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _collect_rows(
        self,
        data: List[ScanSignatureEntry],
        row_factory: Callable[[ScanSignatureEntry], List[CsvRow]],
    ) -> List[CsvRow]:
        rows: List[CsvRow] = []
        for entry in data:
            rows.extend(row_factory(entry))
        return rows

    def save_csv(self, data: List[ScanSignatureEntry], path: Path) -> None:
        rows = self._collect_rows(data, lambda entry: entry.to_csv_rows())
        self._write_csv(path, rows, SAVE_CSV_FIELDNAMES)

    def save_summary_csv(self, data: List[ScanSignatureEntry], path: Path) -> None:
        rows = self._collect_rows(data, lambda entry: [entry.to_summary_row()])
        self._write_csv(path, rows, SUMMARY_CSV_FIELDNAMES)

    def export_all(self, data: List[ScanSignatureEntry]) -> None:
        self.save_json(data, self.output_dir / "scan_signatures.json")
        self.save_csv(data, self.output_dir / "scan_signatures.csv")
        self.save_summary_csv(data, self.output_dir / "scan_signatures_summary.csv")


# Preserve the module-level public API for existing callers.
_default_exporter = ScanSignatureExporter()


def save_json(data: List[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_json(data, path)


def save_csv(data: List[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_csv(data, path)


def save_summary_csv(data: List[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_summary_csv(data, path)


def main() -> None:
    data = asyncio.run(scrape_scan_signatures())
    _default_exporter.export_all(data)
    print(
        f"Saved {len(data)} minerals to {OUTPUT_DIR}/scan_signatures.json, .csv, and scan_signatures_summary.csv"
    )


if __name__ == "__main__":
    main()
