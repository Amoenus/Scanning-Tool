"""Application-wide event signals for the scanning tool."""

from blinker import Signal

status_updated: Signal = Signal("status_updated")
sync_capture_sliders_signal: Signal = Signal("sync_capture_sliders")
update_capture_overlay_region_signal: Signal = Signal("update_capture_overlay_region")
alignment_applied_signal: Signal = Signal("alignment_applied")
ollama_status_updated: Signal = Signal("ollama_status_updated")
ollama_readiness_changed: Signal = Signal("ollama_readiness_changed")
