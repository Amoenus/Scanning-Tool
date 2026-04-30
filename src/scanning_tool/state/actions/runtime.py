from enum import StrEnum


class RuntimeAction(StrEnum):
    """Actions specific to the Runtime status concern."""

    RESTART_OLLAMA = "restart_ollama"
    MANUAL_REALIGN = "manual_realign"
