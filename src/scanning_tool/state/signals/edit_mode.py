from blinker import Signal

edit_mode_changed: Signal = Signal("edit_mode_changed")
region_drafted: Signal = Signal("region_drafted")
region_committed: Signal = Signal("region_committed")

__all__ = [
    "edit_mode_changed",
    "region_drafted",
    "region_committed",
]
