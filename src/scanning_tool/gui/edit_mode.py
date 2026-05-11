"""Toolkit-agnostic edit-mode renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EditModeRenderer(ABC):
    """Renderer interface for edit-mode interactions."""

    @abstractmethod
    def install(self) -> None:
        """Install the edit-mode renderer and set up necessary resources."""
        raise NotImplementedError

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the edit-mode renderer and clean up any resources used."""
        raise NotImplementedError
