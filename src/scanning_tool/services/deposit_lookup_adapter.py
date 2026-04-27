from __future__ import annotations

from re import Pattern
from typing import TYPE_CHECKING

from scanning_tool.deposits import lookup_deposit
from scanning_tool.interfaces.capture import DepositLookupProvider

if TYPE_CHECKING:
    from scanning_tool.domain.capture import DepositInfo
class DepositLookupAdapter(DepositLookupProvider):
    """Adapter for deposit lookup from OCR code extraction."""

    def __init__(self, code_re: Pattern[str]) -> None:
        self._code_re = code_re

    def lookup(self, code: str | None) -> DepositInfo | None:
        return lookup_deposit(code, self._code_re)
