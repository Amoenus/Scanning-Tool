"""Shared interface definitions for the scanning tool architecture."""

from typing import Protocol


class IService(Protocol):
    """Base protocol for all background and functional services."""

    def start(self) -> None:
        """Starts the service."""
        ...

    def stop(self) -> None:
        """Stops the service."""
        ...
