"""Models and helpers for scraping scan signature entries from SCMDB."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

COLOR_CATEGORY_MAP: dict[str, str] = {
    "rgb(255, 170, 51)": "legendary",
    "rgb(204, 102, 255)": "epic",
    "rgb(51, 153, 255)": "rare",
    "rgb(51, 204, 170)": "uncommon",
    "rgb(136, 153, 170)": "common",
    "rgb(102, 221, 170)": "ROC Mineables",
    "rgb(119, 187, 221)": "FPS Mineables",
    "rgb(170, 153, 119)": "Salvage",
}


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
class ScanSignatureSummary:
    mineral: Optional[str]
    category: str
    base_value: Optional[int]
    max_multiplier: Optional[int]

    def to_csv_row(self) -> CsvRow:
        return {
            "mineral": self.mineral,
            "category": self.category,
            "base_value": self.base_value,
            "max_multiplier": self.max_multiplier,
        }

    @classmethod
    def from_entry(cls, entry: "ScanSignatureEntry") -> "ScanSignatureSummary":
        return cls(
            mineral=entry.mineral,
            category=entry.category,
            base_value=entry._find_base_value(),
            max_multiplier=entry._find_max_multiplier(),
        )


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
        return ScanSignatureSummary.from_entry(self).to_csv_row()

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
    return COLOR_CATEGORY_MAP.get(color, color)


class ScanSignatureEntryFactory:
    @staticmethod
    def _as_optional_str(value: object | None) -> Optional[str]:
        return value if isinstance(value, str) else None

    @staticmethod
    def _create_scan_value(raw_value: RawScanValue) -> ScanValue:
        return ScanValue(
            text=ScanSignatureEntryFactory._as_optional_str(raw_value.get("text")),
            title=ScanSignatureEntryFactory._as_optional_str(raw_value.get("title")),
            amount=raw_value.get("amount"),
            value=raw_value.get("value"),
        )

    @classmethod
    def from_raw_entry(cls, raw_entry: RawScanSignatureEntry) -> ScanSignatureEntry:
        raw_values = raw_entry.get("values") or []
        values = [cls._create_scan_value(raw_value) for raw_value in raw_values]

        color = cls._as_optional_str(raw_entry.get("color"))
        return ScanSignatureEntry(
            mineral=cls._as_optional_str(raw_entry.get("mineral")),
            color=color,
            values=values,
            category=parse_color_to_category(color or ""),
        )
