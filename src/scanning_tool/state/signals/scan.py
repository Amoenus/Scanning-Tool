from blinker import Signal

scan_requested: Signal = Signal("scan_requested")
scan_started: Signal = Signal("scan_started")
scan_completed: Signal = Signal("scan_completed")
scan_failed: Signal = Signal("scan_failed")
continuous_mode_changed: Signal = Signal("continuous_mode_changed")
