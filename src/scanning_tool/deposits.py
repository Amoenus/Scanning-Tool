"""Deposit lookup tables, ore tiers, and multiplier code logic."""

import json
from loguru import logger
import re
from typing import Dict, List, Optional

from scanning_tool.config import ROCK_TYPE_FILE
from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config
from scanning_tool.domain.models import (
    DepositLookup,
    DepositTable,
    OreTableEntry,
    OreTier,
    OreTierInfo,
    OreValueInfo,
    RockDeposit,
    ScanSignature,
)



# --- Dynamic scan signature table ---
import pandas as pd
from pathlib import Path

# Path to the summary CSV (relative to project root)
SCAN_SIG_CSV = Path(__file__).parent.parent.parent / "csv" / "scansig" / "scan_signatures_summary.csv"

SCAN_SIGNATURES: Dict[int, ScanSignature] = {}
if SCAN_SIG_CSV.exists():
    try:
        df = pd.read_csv(SCAN_SIG_CSV)
        for _, row in df.iterrows():
            try:
                base_value = int(row["base_value"])
                max_multiplier = int(row["max_multiplier"])
                mineral = row["mineral"]
                category = row["category"]
                SCAN_SIGNATURES[base_value] = {
                    "name": mineral,
                    "category": category,
                    "base_value": base_value,
                    "max_multiplier": max_multiplier,
                }
            except Exception as e:
                logger.warning(f"Bad scan signature row: {row} ({e})")
    except Exception as e:
        logger.warning(f"Failed to load scan signature CSV: {e}")
else:
    logger.warning(f"Scan signature CSV not found: {SCAN_SIG_CSV}")

ORE_TIERS: Dict[OreTier, OreTierInfo] = {
    "HIGHEST": OreTierInfo(ores=["QUANTANIUM", "STILERON", "RICCITE"], color="#E88AFF"),
    "HIGH": OreTierInfo(ores=["TARANITE", "BEXALITE", "GOLD"], color="#63E64C"),
    "MEDIUM": OreTierInfo(ores=["LARANITE", "BORASE", "BERYL", "AGRICIUM", "HEPHAESTANITE"], color="#E6E14C"),
    "LOW": OreTierInfo(ores=["TUNGSTEN", "TITANIUM", "SILICON", "IRON", "QUARTZ", "CORUNDUM", "COPPER", "TIN", "ALUMINUM", "ICE"], color="#E69E4C"),
}

ORE_VALUE_MAP: Dict[str, OreValueInfo] = {}
for _tier, _data in ORE_TIERS.items():
    for _ore in _data.ores:
        ORE_VALUE_MAP[_ore.upper()] = {"tier": _tier, "color": _data.color}

_TIER_ORDER: List[OreTier] = ["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


def build_deposit_tables(rock_data: Dict[str, RockDeposit]) -> Dict[str, DepositTable]:
    """Build per-deposit ore tables for one region's rock data."""
    deposit_tables: Dict[str, DepositTable] = {}
    for deposit_name, details in rock_data.items():
        ores = details.get("ores", {})
        table: DepositTable = []
        for ore_name, ore_data in ores.items():
            name_up = ore_name.upper()
            value_info: OreValueInfo = ORE_VALUE_MAP.get(name_up, {"tier": "OTHER", "color": "#888"})
            entry: OreTableEntry = {
                "name": ore_name.title(),
                "prob": f"{ore_data.get('prob', 0) * 100:.0f}%",
                "min": f"{ore_data.get('minPct', 0) * 100:.0f}%",
                "max": f"{ore_data.get('maxPct', 0) * 100:.0f}%",
                "med": f"{ore_data.get('medPct', 0) * 100:.0f}%",
                "tier": value_info["tier"],
                "color": value_info["color"],
            }
            table.append(entry)
        table.sort(key=lambda x: _TIER_ORDER.index(x["tier"]))
        deposit_tables[deposit_name.upper()] = table
    return deposit_tables


def load_rock_data() -> None:
    """Load RockType.json and build deposit tables into app_state."""
    with open(ROCK_TYPE_FILE, "r") as f:
        service_state.rock_data = json.load(f)

    service_state.deposit_tables = {
        region_name.upper(): build_deposit_tables(region_data)
        for region_name, region_data in service_state.rock_data.items()
    }



def lookup_deposit(code: Optional[str]) -> Optional[DepositLookup]:
    """Look up a deposit by its numeric code using scraped scan signature data."""
    if not code:
        return None
    try:
        m = re.search(r"(\d+)$", code)
        if not m:
            return None
        num_code = int(m.group(1))
        for base_value, info in SCAN_SIGNATURES.items():
            if num_code % base_value == 0:
                deposits = num_code // base_value
                return {
                    "name": info["name"],
                    "base_code": base_value,
                    "deposits": deposits,
                    "category": info["category"],
                    "max_multiplier": info["max_multiplier"],
                }
    except Exception:
        pass
    return None


def extract_code_from_text(raw_text: str):
    """Extract a deposit code from OCR text."""
    if not raw_text:
        return None, None
    matches = service_state.code_re.findall(raw_text)
    if not matches:
        return None, raw_text
    raw = matches[0].upper()
    if any(ch.isdigit() for ch in raw):
        m = re.match(r"([A-Za-z]?-?)([\d,\.]+)", raw)
        if m:
            prefix, digits = m.groups()
            digits = digits.replace(",", "").replace(".", "")
            candidate = prefix + digits
        else:
            candidate = raw.replace(",", "").replace(".", "")
    else:
        candidate = raw
    return candidate, raw
