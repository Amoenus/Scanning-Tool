"""Domain DTOs for raw external data shapes."""

from __future__ import annotations

from typing import TypedDict


class ScanSignatureCSVRowData(TypedDict, total=False):
    """Typed shape for one row of scan signature CSV input."""

    mineral: str
    category: str
    base_value: str | int | float
    max_multiplier: str | int | float
