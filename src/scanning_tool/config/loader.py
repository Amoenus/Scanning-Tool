"""Configuration constants and resource locators."""

import sys
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_FILE = PROJECT_ROOT / "config.json"
ROCK_TYPE_FILENAME = "RockType.json"
ROCK_TYPE_FILE = PROJECT_ROOT / ROCK_TYPE_FILENAME

def resource_path(relative_path: str) -> str:
    """Get absolute path to a resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(PROJECT_ROOT / relative_path)

def ensure_anchor_directory(path: str) -> None:
    """Ensure the directory for anchor templates exists."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.warning(f"Unable to ensure anchor template directory {path}: {exc}")
