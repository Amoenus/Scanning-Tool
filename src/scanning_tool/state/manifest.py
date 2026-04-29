from dataclasses import dataclass, field
from typing import Any

from blinker import Signal


@dataclass(frozen=True)
class ConcernManifest:
    """Declares which concerns a UI claims, and its exact vocabulary usage."""

    claimed_concerns: frozenset[str] = field(default_factory=frozenset)
    published_actions: frozenset[Any] = field(default_factory=frozenset)
    subscribed_signals: frozenset[Signal] = field(default_factory=frozenset)
