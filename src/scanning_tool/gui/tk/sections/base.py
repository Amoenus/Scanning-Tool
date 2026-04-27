"""Common types for GUI sections."""
from __future__ import annotations


import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Protocol

from scanning_tool.gui.context import GuiSectionDependencies



from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..theme import GlassPalette
    from ..status import StatusBar
@dataclass(frozen=True)
class SectionContext(GuiSectionDependencies):
    """Tk-specific section context built on shared GUI dependencies."""

    root: tk.Tk
    colors: GlassPalette
    status: StatusBar


class Section(Protocol):
    """A UI section — one LabelFrame, self-contained widgets and callbacks."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.Frame: ...
