"""Common types for GUI sections."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import TYPE_CHECKING, Protocol

from scanning_tool.gui.context import GuiSectionDependencies

if TYPE_CHECKING:
    from ..status import StatusBar
    from ..theme import GlassPalette


@dataclass(frozen=True)
class SectionContext(GuiSectionDependencies):
    """Tk-specific section context built on shared GUI dependencies."""

    root: tk.Tk
    colors: GlassPalette
    status: StatusBar


class Section(Protocol):
    """A UI section — one LabelFrame, self-contained widgets and callbacks."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.Frame: ...
