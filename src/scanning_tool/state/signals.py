"""Application-wide event signals for the scanning tool."""

from blinker import Signal

status_updated: Signal = Signal("status_updated")
sync_capture_sliders_signal: Signal = Signal("sync_capture_sliders")
update_capture_overlay_region_signal: Signal = Signal("update_capture_overlay_region")
