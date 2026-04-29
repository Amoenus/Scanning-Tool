from dataclasses import dataclass

@dataclass(frozen=True)
class EventLogReadModel:
    """Read model for the Event log concern."""
    logs: list[str] = None
