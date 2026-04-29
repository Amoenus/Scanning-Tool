from blinker import Signal

event_log_emitted: Signal = Signal("event_log_emitted")
raw_log_emitted: Signal = Signal("raw_log_emitted")

__all__ = [
    "event_log_emitted",
    "raw_log_emitted",
]
