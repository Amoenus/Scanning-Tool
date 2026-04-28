"""Configuration package wrapper for the scanning tool."""

from scanning_tool.config.loader import (
    CONFIG_FILE,
    PROJECT_ROOT,
    ROCK_TYPE_FILE,
    ROCK_TYPE_FILENAME,
    ensure_anchor_directory,
    resource_path,
)

__all__ = [
    "CONFIG_FILE",
    "PROJECT_ROOT",
    "ROCK_TYPE_FILE",
    "ROCK_TYPE_FILENAME",
    "ensure_anchor_directory",
    "resource_path",
]
