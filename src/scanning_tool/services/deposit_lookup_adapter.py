from __future__ import annotations

from typing import Optional, Pattern

from scanning_tool.domain.capture import DepositInfo
from scanning_tool.interfaces.capture import DepositLookupProvider
from scanning_tool.deposits import lookup_deposit


class DepositLookupAdapter(DepositLookupProvider):
    """Adapter for deposit lookup from OCR code extraction."""

    def __init__(self, code_re: Pattern[str]) -> None:
        self._code_re = code_re

    def lookup(self, code: Optional[str]) -> Optional[DepositInfo]:
        return lookup_deposit(code, self._code_re)
