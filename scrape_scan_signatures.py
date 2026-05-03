"""Fetch scan signature data from the SCMDB JSON API.

Retrieves mineral name, scan values, rarity/category from the SCMDB
mining_data JSON endpoint rather than scraping the rendered HTML overlay.
Outputs JSON and CSV formats identical to the previous implementation.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from scanning_tool.deposits.scan_signature_scraper import (
    CsvRow,
    MineableElementJSON,
    MiningDataJSON,
    ScanSignatureEntry,
    ScanSignatureEntryFactory,
    _SENTINEL_ENTRIES,
    load_manual_overrides,
)

OUTPUT_DIR = Path("csv/scansig")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VERSIONS_URL = "https://scmdb.net/data/versions.json"
MINING_DATA_URL_TEMPLATE = "https://scmdb.net/data/mining_data-{version}.json"


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ORCA-scraper/1.0)",
    "Accept": "application/json",
}


def _fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers=_HEADERS)  # noqa: S310
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _resolve_mining_data_url() -> str:
    """Fetch the versions list and return the URL for the latest mining_data JSON."""
    versions = _fetch_json(VERSIONS_URL)
    if not isinstance(versions, list) or not versions:
        msg = f"Unexpected versions payload from {VERSIONS_URL}"
        raise ValueError(msg)
    latest_version: str = versions[0]["version"]
    return MINING_DATA_URL_TEMPLATE.format(version=latest_version)


def _parse_mining_data(raw: object) -> list[ScanSignatureEntry]:
    data = MiningDataJSON.model_validate(raw)

    ship_entries: list[ScanSignatureEntry] = []
    for element in data.mineableElements.values():
        entry = ScanSignatureEntryFactory.from_json_element(element)
        if entry is not None:
            ship_entries.append(entry)

    # Sort ship-mineable entries by base scan signature value (ascending).
    ship_entries.sort(key=lambda e: e.base_value or 0)

    sentinel_entries = [
        ScanSignatureEntryFactory.sentinel_entry(name, category, base_value, max_mult)
        for name, category, base_value, max_mult in _SENTINEL_ENTRIES
    ]

    return ship_entries + sentinel_entries


def fetch_scan_signatures() -> list[ScanSignatureEntry]:
    """Fetch and parse all scan signature entries from the SCMDB JSON API.

    Hand-curated entries from manual_overrides.json are merged in after
    the scraped data so they survive re-scrapes unchanged.
    """
    url = _resolve_mining_data_url()
    raw = _fetch_json(url)
    scraped = _parse_mining_data(raw)
    manual = load_manual_overrides()
    return scraped + manual


# ---------------------------------------------------------------------------
# Exporter (unchanged public API)
# ---------------------------------------------------------------------------


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
    data = fetch_scan_signatures()
    _default_exporter.export_all(data)
    print(
        f"Saved {len(data)} minerals to {OUTPUT_DIR}/scan_signatures.json, "
        ".csv, and scan_signatures_summary.csv",
    )


if __name__ == "__main__":
    main()
