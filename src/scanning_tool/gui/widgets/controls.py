"""Control widgets for the scanning tool GUI."""

from typing import Callable, Optional, Tuple

import tkinter as tk
from tkinter import ttk

GlassScaleCommand = Callable[[str], None]


def create_section_row(parent: ttk.Widget, pady: Tuple[int, int] = (0, 5)) -> ttk.Frame:
    """Create a styled row container for section controls."""
    row = ttk.Frame(parent, style="Glass.Section.TFrame")
    row.pack(fill="x", padx=5, pady=pady)
    return row


def _format_glass_scale_value(value: float, resolution: float) -> str:
    if resolution and resolution < 1.0:
        return f"{value:.2f}"
    return f"{int(round(value))}"


def _coerce_glass_scale_value(raw_value: str, default_value: float) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return default_value


def _snap_glass_scale_value(value: float, resolution: float) -> float:
    return round(value / resolution) * resolution if resolution else value


def create_glass_scale(
    parent: ttk.Widget,
    *,
    text: str,
    minimum: float,
    maximum: float,
    initial: float,
    command: Optional[GlassScaleCommand],
    resolution: float = 1.0,
    padding: Tuple[int, int] = (0, 4),
) -> ttk.Scale:
    """Create a labeled ttk.Scale with the custom glass styling."""
    container = ttk.Frame(parent, style="Glass.Section.TFrame")
    container.pack(fill="x", padx=4, pady=padding)

    value_var = tk.DoubleVar(value=initial)
    label_var = tk.StringVar(value=f"{text}: {_format_glass_scale_value(initial, resolution)}")
    ttk.Label(container, textvariable=label_var, style="Glass.Small.TLabel").pack(
        anchor="w", padx=2
    )

    def on_change(raw_value: str) -> None:
        numeric = _coerce_glass_scale_value(raw_value, value_var.get())
        snapped = _snap_glass_scale_value(numeric, resolution)

        if abs(snapped - value_var.get()) > 1e-9:
            value_var.set(snapped)

        label_var.set(f"{text}: {_format_glass_scale_value(snapped, resolution)}")

        if command is not None:
            command(_format_glass_scale_value(snapped, resolution))

    scale = ttk.Scale(
        container,
        from_=minimum,
        to=maximum,
        orient="horizontal",
        variable=value_var,
        command=on_change,
        style="Glass.Horizontal.TScale",
    )
    scale.pack(fill="x", padx=2, pady=(2, 0))

    def update_label(*_: object) -> None:
        value = value_var.get()
        label_var.set(f"{text}: {_format_glass_scale_value(value, resolution)}")

    value_var.trace_add("write", update_label)

    scale._glass_container = container  # type: ignore[attr-defined]
    scale._glass_value_var = value_var  # type: ignore[attr-defined]
    scale._glass_label_var = label_var  # type: ignore[attr-defined]
    scale._glass_command = command  # type: ignore[attr-defined]
    scale._glass_resolution = resolution  # type: ignore[attr-defined]

    return scale


def create_button_row(
    parent: ttk.Widget,
    buttons: list[tuple[str, Callable[[], None]]],
    style: str = "Glass.TButton",
) -> ttk.Frame:
    """Create a row of buttons with equal spacing."""
    row = create_section_row(parent)
    for label, command in buttons:
        ttk.Button(row, text=label, command=command, style=style).pack(
            side="left", padx=5
        )
    return row
