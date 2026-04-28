"""Scrape Scan Signature Identifier data from https://scmdb.net/?page=mine
Extracts mineral name, scan values, rarity/color, and category from the overlay.
Outputs JSON and CSV formats.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
from playwright.async_api import Page, async_playwright

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scanning_tool.deposits.scan_signature_scraper import (  # noqa: E402
    CsvRow,
    RawScanSignatureEntry,
    ScanSignatureEntry,
    ScanSignatureEntryFactory,
)

OUTPUT_DIR = Path("csv/scansig")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://scmdb.net/?page=mine"


SCRAPE_SIGNATURES_SCRIPT = r"""() => {
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


class ScanSignatureScraper:
    """Scrape scan signature entries from the SCMDB overlay."""

    def __init__(self, target_url: str = TARGET_URL) -> None:
        self._target_url = target_url

    async def _evaluate_scan_signature_overlay(
        self, page: Page,
    ) -> list[RawScanSignatureEntry]:
        await page.click('button[title^="Scan Signature Identifier"]')
        await page.wait_for_selector(".sigchart-overlay", timeout=10000)
        return await page.evaluate(SCRAPE_SIGNATURES_SCRIPT)

    def _build_scan_signature_entries(
        self, raw_data: list[RawScanSignatureEntry],
    ) -> list[ScanSignatureEntry]:
        return [
            ScanSignatureEntryFactory.from_raw_entry(raw_entry)
            for raw_entry in raw_data
        ]

    async def scrape(self) -> list[ScanSignatureEntry]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self._target_url, wait_until="networkidle")

            raw_data = await self._evaluate_scan_signature_overlay(page)
            entries = self._build_scan_signature_entries(raw_data)

            await browser.close()
            return entries


async def scrape_scan_signatures() -> list[ScanSignatureEntry]:
    return await ScanSignatureScraper().scrape()


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

    def _write_dataframe(
        self, df: pd.DataFrame, path: Path, *, as_csv: bool = True,
    ) -> None:
        if as_csv:
            df.to_csv(path, index=False, encoding="utf-8")
        else:
            path.write_text(
                df.to_json(orient="records", force_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _dataframe_from_rows(self, rows: list[CsvRow]) -> pd.DataFrame:
        return pd.DataFrame.from_records(rows)

    def save_json(self, data: list[ScanSignatureEntry], path: Path) -> None:
        rows = [asdict(entry) for entry in data]
        self._write_dataframe(pd.DataFrame.from_records(rows), path, as_csv=False)

    def save_csv(self, data: list[ScanSignatureEntry], path: Path) -> None:
        rows = [row for entry in data for row in entry.to_csv_rows()]
        self._write_dataframe(self._dataframe_from_rows(rows), path)

    def save_summary_csv(self, data: list[ScanSignatureEntry], path: Path) -> None:
        rows = [entry.to_summary_row() for entry in data]
        self._write_dataframe(self._dataframe_from_rows(rows), path)

    def export_all(self, data: list[ScanSignatureEntry]) -> None:
        self.save_json(data, self.output_dir / "scan_signatures.json")
        self.save_csv(data, self.output_dir / "scan_signatures.csv")
        self.save_summary_csv(data, self.output_dir / "scan_signatures_summary.csv")


# Preserve the module-level public API for existing callers.
_default_exporter = ScanSignatureExporter()


def save_json(data: list[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_json(data, path)


def save_csv(data: list[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_csv(data, path)


def save_summary_csv(data: list[ScanSignatureEntry], path: Path) -> None:
    _default_exporter.save_summary_csv(data, path)


def main() -> None:
    data = asyncio.run(scrape_scan_signatures())
    _default_exporter.export_all(data)
    print(
        f"Saved {len(data)} minerals to {OUTPUT_DIR}/scan_signatures.json, .csv, and scan_signatures_summary.csv",
    )


if __name__ == "__main__":
    main()
