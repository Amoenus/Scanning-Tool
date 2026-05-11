"""Input widgets for the scanning tool GUI."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import TYPE_CHECKING

from .controls import ResponsivePairRow, create_section_row

if TYPE_CHECKING:
    from ..theme import GlassPalette


def create_labeled_spinbox(
    parent: ttk.Widget,
    text: str,
    variable: tk.Variable,
    from_: float,
    to: float,
    increment: float,
    width: int,
    command: Callable[[], object] | str | list[str] | tuple[str, ...] | None,
    colors: GlassPalette,
) -> tk.Spinbox:
    """Create a labeled spinbox row with custom glass styling."""
    row = ResponsivePairRow(parent)
    label = ttk.Label(row, text=text, style="Glass.Small.TLabel")

    spinbox = tk.Spinbox(
        row,
        from_=from_,
        to=to,
        increment=increment,
        textvariable=variable,
        width=width,
        command=command if command is not None else "",
    )
    row.set_widgets(label, spinbox)

    from ..theme import style_spinbox

    style_spinbox(spinbox, colors)

    return spinbox


def create_labeled_entry(
    parent: ttk.Widget,
    text: str,
    variable: tk.Variable,
) -> tk.Entry:
    """Create a labeled entry row with the custom glass styling."""
    row = ResponsivePairRow(parent)
    label = ttk.Label(row, text=text, style="Glass.Small.TLabel")

    entry = tk.Entry(row, textvariable=variable, width=1)
    row.set_widgets(label, entry)
    return entry


def create_status_label(parent: ttk.Widget, variable: tk.Variable) -> ttk.Label:
    """Create a styled status label row for section text feedback."""
    row = create_section_row(parent, pady=(0, 2))
    label = ttk.Label(
        row,
        textvariable=variable,
        style="Glass.Small.TLabel",
        justify="left",
    )
    label.pack(fill="x", padx=5)
    return label


def create_labeled_combobox(
    parent: ttk.Widget,
    text: str,
    variable: tk.Variable,
    values: list[str],
    width: int = 1,
) -> ttk.Combobox:
    """Create a labeled combobox row with the custom glass styling."""
    row = ResponsivePairRow(parent)
    label = ttk.Label(row, text=text, style="Glass.Small.TLabel")

    combobox = ttk.Combobox(row, textvariable=variable, values=values, width=width)
    row.set_widgets(label, combobox)
    return combobox
