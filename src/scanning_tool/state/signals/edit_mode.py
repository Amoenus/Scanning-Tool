from blinker import Signal

edit_mode_toggled: Signal = Signal("edit_mode_toggled")

__all__ = [
    "edit_mode_toggled",
]
