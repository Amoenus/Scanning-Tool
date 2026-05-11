"""Shared Qt section types for the scanning tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PyQt6.QtWidgets import QWidget

from scanning_tool.gui.context import GuiSectionDependencies
from scanning_tool.gui.qt.status import StatusBar


@dataclass(frozen=True)
class SectionContext(GuiSectionDependencies):
    """Qt-specific section context built on shared GUI dependencies."""

    root: QWidget
    status: StatusBar


class Section(Protocol):
    """A UI section — one self-contained widget tree."""

    def build(self, parent: QWidget, ctx: SectionContext) -> QWidget: ...
