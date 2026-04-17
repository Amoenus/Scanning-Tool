"""Deposit lookup, ore tiers, and code extraction."""

from scanning_tool.deposits.lookup import extract_code_from_text, lookup_deposit
from scanning_tool.deposits.ore_tiers import ORE_TIERS, ORE_VALUE_MAP, TIER_ORDER
from scanning_tool.deposits.scan_signatures import SCAN_SIGNATURES
from scanning_tool.deposits.tables import build_deposit_tables, load_rock_data

__all__ = [
    "extract_code_from_text",
    "lookup_deposit",
    "ORE_TIERS",
    "ORE_VALUE_MAP",
    "TIER_ORDER",
    "SCAN_SIGNATURES",
    "build_deposit_tables",
    "load_rock_data",
]
