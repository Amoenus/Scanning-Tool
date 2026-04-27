"""Common types for GUI sections."""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Protocol

from scanning_tool.gui.context import GuiSectionDependencies

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
