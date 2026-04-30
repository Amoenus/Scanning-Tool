"""Toolkit-agnostic edit-mode renderer interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.gui.state import OverlayState, ControlState


class EditModeRenderer(ABC):
    """Renderer interface for edit-mode interactions."""

    @abstractmethod
    def install(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def destroy(self) -> None:
        raise NotImplementedError
