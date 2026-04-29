"""Runtime status concern signals."""
from blinker import Signal

status_updated: Signal = Signal("status_updated")
alignment_info_updated: Signal = Signal("alignment_info_updated")
ollama_status_updated: Signal = Signal("ollama_status_updated")
ollama_readiness_changed: Signal = Signal("ollama_readiness_changed")

alignment_requested: Signal = Signal("alignment_requested")
alignment_failed: Signal = Signal("alignment_failed")
alignment_reset: Signal = Signal("alignment_reset")
alignment_applied_signal: Signal = Signal("alignment_applied")

__all__ = [
    "status_updated",
    "alignment_info_updated",
    "ollama_status_updated",
    "ollama_readiness_changed",
    "alignment_requested",
    "alignment_failed",
    "alignment_reset",
    "alignment_applied_signal",
]
