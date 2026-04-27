"""Models and helpers for scraping scan signature entries from SCMDB."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

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


class RawScanValue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str | None = None
    title: str | None = None
    amount: int | None = None
    value: int | None = None


class RawScanSignatureEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mineral: str | None = None
    color: str | None = None
    values: list[RawScanValue] = Field(default_factory=list)


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
                mineral=self.mineral, category=self.category, color=self.color,
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
        max_multiplier: int | None = None
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
    def _create_scan_value(raw_value: RawScanValue | dict[str, object]) -> ScanValue:
        validated = RawScanValue.model_validate(raw_value)
        return ScanValue(
            text=validated.text,
            title=validated.title,
            amount=validated.amount,
            value=validated.value,
        )

    @classmethod
    def from_raw_entry(
        cls, raw_entry: RawScanSignatureEntry | dict[str, object],
    ) -> ScanSignatureEntry:
        validated = RawScanSignatureEntry.model_validate(raw_entry)
        values = [cls._create_scan_value(raw_value) for raw_value in validated.values]

        return ScanSignatureEntry(
            mineral=validated.mineral,
            color=validated.color,
            values=values,
            category=parse_color_to_category(validated.color or ""),
        )
