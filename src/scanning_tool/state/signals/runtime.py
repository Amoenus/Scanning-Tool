"""Runtime status concern signals."""
from blinker import Signal

status_updated: Signal = Signal("status_updated")
alignment_info_updated: Signal = Signal("alignment_info_updated")
ollama_status_updated: Signal = Signal("ollama_status_updated")
ollama_readiness_changed: Signal = Signal("ollama_readiness_changed")

__all__ = [
    "status_updated",
    "alignment_info_updated",
    "ollama_status_updated",
    "ollama_readiness_changed",
]
