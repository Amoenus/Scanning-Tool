"""Models and helpers for fetching scan signature entries from the SCMDB JSON API."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# Maps rarity tier to the CSS colour used by the SCMDB overlay (kept for CSV
# compatibility so downstream consumers that read the colour column still work).
RARITY_COLOR_MAP: dict[str, str] = {
    "legendary": "rgb(255, 170, 51)",
    "epic": "rgb(204, 102, 255)",
    "rare": "rgb(51, 153, 255)",
    "uncommon": "rgb(51, 204, 170)",
    "common": "rgb(136, 153, 170)",
    "ROC Mineables": "rgb(102, 221, 170)",
    "FPS Mineables": "rgb(119, 187, 221)",
    "Salvage": "rgb(170, 153, 119)",
}

# Reverse map kept for callers that previously used COLOR_CATEGORY_MAP.
COLOR_CATEGORY_MAP: dict[str, str] = {v: k for k, v in RARITY_COLOR_MAP.items()}

# Number of ×N multiplier steps shown in the overlay per rarity tier.
RARITY_MAX_MULTIPLIER: dict[str, int] = {
    "legendary": 2,
    "epic": 3,
    "rare": 4,
    "uncommon": 5,
    "common": 6,
}

# Sentinel entries for grouped categories that are not individually distinguished
# in the game UI overlay.  Values taken from the historical scraped CSV.
_SENTINEL_ENTRIES: list[tuple[str, str, int, int]] = [
    # (name, category, base_value, max_multiplier)
    ("ROC Mineables", "ROC Mineables", 4000, 7),
    ("FPS Mineables", "FPS Mineables", 3000, 10),
    ("Salvage", "Salvage", 2000, 15),
]

_STRIP_SUFFIX_RE = re.compile(r"\s*\((?:Ore|Raw)\)\s*$", re.IGNORECASE)


def _strip_mineral_suffix(name: str) -> str:
    """Remove trailing '(Ore)' / '(Raw)' qualifiers from a mineral name."""
    return _STRIP_SUFFIX_RE.sub("", name).strip()


# ---------------------------------------------------------------------------
# JSON models
# ---------------------------------------------------------------------------


class MineableElementJSON(BaseModel):
    """One entry from the ``mineableElements`` dict in the SCMDB mining_data JSON."""

    model_config = ConfigDict(extra="ignore")

    name: str
    rarity: str | None = None
    scanSignature: int | None = None
    groundScanSignature: int | None = None
    fpsScanSignature: int | None = None


class MiningDataJSON(BaseModel):
    """Top-level structure of ``mining_data-{version}.json``."""

    model_config = ConfigDict(extra="ignore")

    mineableElements: dict[str, MineableElementJSON] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Output models (public API – unchanged from the previous HTML-based scraper)
# ---------------------------------------------------------------------------

CsvRow = dict[str, str | int | None]


@dataclass(frozen=True)
class ScanValue:
    text: str | None
    title: str | None
    amount: int | None
    value: int | None

    def to_csv_row(
        self,
        mineral: str | None,
        category: str,
        color: str | None,
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
class ScanSignatureSummary:
    mineral: str | None
    category: str
    base_value: int | None
    max_multiplier: int | None

    def to_csv_row(self) -> CsvRow:
        return {
            "mineral": self.mineral,
            "category": self.category,
            "base_value": self.base_value,
            "max_multiplier": self.max_multiplier,
        }

    @classmethod
    def from_entry(cls, entry: ScanSignatureEntry) -> ScanSignatureSummary:
        return cls(
            mineral=entry.mineral,
            category=entry.category,
            base_value=entry.base_value,
            max_multiplier=entry.max_multiplier,
        )


@dataclass(frozen=True)
class ScanSignatureEntry:
    mineral: str | None
    color: str | None
    values: list[ScanValue]
    category: str

    def to_csv_rows(self) -> list[CsvRow]:
        return [
            value.to_csv_row(
                mineral=self.mineral,
                category=self.category,
                color=self.color,
            )
            for value in self.values
        ]

    def to_summary_row(self) -> CsvRow:
        return ScanSignatureSummary.from_entry(self).to_csv_row()

    @property
    def base_value(self) -> int | None:
        for value in self.values:
            if value.amount == 1:
                return value.value
        return self.values[0].value if self.values else None

    @property
    def max_multiplier(self) -> int | None:
        result: int | None = None
        for value in self.values:
            if value.amount is not None and (result is None or value.amount > result):
                result = value.amount
        return result


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def parse_color_to_category(color: str) -> str:
    """Map an RGB color string to a rarity/category string."""
    return COLOR_CATEGORY_MAP.get(color, color)


def _build_values(mineral: str, base_value: int, max_multiplier: int) -> list[ScanValue]:
    """Generate the ×N pill values for a mineral given its base scan signature."""
    values = []
    for n in range(1, max_multiplier + 1):
        total = base_value * n
        total_fmt = f"{total:,}"
        text = total_fmt
        title = f"{mineral} \u00d7{n} = {total_fmt}"
        values.append(ScanValue(text=text, title=title, amount=n, value=total))
    return values


MANUAL_OVERRIDES_PATH = Path(__file__).parents[3] / "csv" / "scansig" / "manual_overrides.json"


def load_manual_overrides(path: Path = MANUAL_OVERRIDES_PATH) -> list[ScanSignatureEntry]:
    """Load hand-curated entries from a JSON override file.

    The override file lives at csv/scansig/manual_overrides.json and is
    intentionally kept outside the scraper so it survives re-scrapes.
    Each entry in ``entries`` becomes a single-pill ScanSignatureEntry.
    Returns an empty list if the file does not exist.
    """
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    result: list[ScanSignatureEntry] = []
    for item in raw.get("entries", []):
        mineral: str = item["mineral"]
        category: str = item["category"]
        color: str | None = item.get("color") or RARITY_COLOR_MAP.get(category)
        amount: int = int(item["amount"])
        value: int = int(item["value"])
        value_fmt = f"{value:,}"
        pill_text = value_fmt
        pill_title = f"{mineral} \u00d7{amount} = {value_fmt}"
        scan_value = ScanValue(text=pill_text, title=pill_title, amount=amount, value=value)
        result.append(ScanSignatureEntry(mineral=mineral, color=color, values=[scan_value], category=category))
    return result


class ScanSignatureEntryFactory:
    @classmethod
    def from_json_element(cls, element: MineableElementJSON) -> ScanSignatureEntry | None:
        """Build a ScanSignatureEntry from a ship-mineable JSON element.

        Returns None if the element does not have a ship scan signature or a
        recognised rarity tier (those are handled separately as sentinel entries).
        """
        if element.scanSignature is None or element.rarity is None:
            return None

        max_mult = RARITY_MAX_MULTIPLIER.get(element.rarity)
        if max_mult is None:
            return None

        mineral = _strip_mineral_suffix(element.name)
        color = RARITY_COLOR_MAP.get(element.rarity)
        values = _build_values(mineral, element.scanSignature, max_mult)

        return ScanSignatureEntry(
            mineral=mineral,
            color=color,
            values=values,
            category=element.rarity,
        )

    @classmethod
    def sentinel_entry(cls, name: str, category: str, base_value: int, max_multiplier: int) -> ScanSignatureEntry:
        """Build a grouped sentinel entry (ROC Mineables, FPS Mineables, Salvage)."""
        color = RARITY_COLOR_MAP.get(category)
        values = _build_values(name, base_value, max_multiplier)
        return ScanSignatureEntry(
            mineral=name,
            color=color,
            values=values,
            category=category,
        )
