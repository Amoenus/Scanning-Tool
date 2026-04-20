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


class GlassScaleController:
    """Encapsulate the custom glass scale widget and its label synchronization."""

    def __init__(
        self,
        parent: ttk.Widget,
        *,
        text: str,
        minimum: float,
        maximum: float,
        initial: float,
        command: Optional[GlassScaleCommand],
        resolution: float,
        padding: Tuple[int, int],
    ) -> None:
        self._text = text
        self._command = command
        self._resolution = resolution

        self._container = ttk.Frame(parent, style="Glass.Section.TFrame")
        self._container.pack(fill="x", padx=4, pady=padding)

        self._value_var = tk.DoubleVar(value=initial)
        self._label_var = tk.StringVar(value=self._create_label(initial))
        ttk.Label(
            self._container,
            textvariable=self._label_var,
            style="Glass.Small.TLabel",
        ).pack(anchor="w", padx=2)

        self._scale = ttk.Scale(
            self._container,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            variable=self._value_var,
            command=self._on_change,
            style="Glass.Horizontal.TScale",
        )
        self._scale.pack(fill="x", padx=2, pady=(2, 0))

        self._value_var.trace_add("write", self._update_label)
        self._attach_metadata()

    @property
    def scale(self) -> ttk.Scale:
        return self._scale

    def _create_label(self, value: float) -> str:
        return f"{self._text}: {self._format_value(value)}"

    def _format_value(self, value: float) -> str:
        if self._resolution and self._resolution < 1.0:
            return f"{value:.2f}"
        return f"{int(round(value))}"

    def _coerce_value(self, raw_value: str) -> float:
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return self._value_var.get()

    def _snap_value(self, value: float) -> float:
        return round(value / self._resolution) * self._resolution if self._resolution else value

    def _on_change(self, raw_value: str) -> None:
        numeric = self._coerce_value(raw_value)
        snapped = self._snap_value(numeric)

        if abs(snapped - self._value_var.get()) > 1e-9:
            self._value_var.set(snapped)

        self._label_var.set(self._create_label(snapped))

        if self._command is not None:
            self._command(self._format_value(snapped))

    def _update_label(self, *_: object) -> None:
        self._label_var.set(self._create_label(self._value_var.get()))

    def _attach_metadata(self) -> None:
        self._scale._glass_container = self._container  # type: ignore[attr-defined]
        self._scale._glass_value_var = self._value_var  # type: ignore[attr-defined]
        self._scale._glass_label_var = self._label_var  # type: ignore[attr-defined]
        self._scale._glass_command = self._command  # type: ignore[attr-defined]
        self._scale._glass_resolution = self._resolution  # type: ignore[attr-defined]


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
    controller = GlassScaleController(
        parent,
        text=text,
        minimum=minimum,
        maximum=maximum,
        initial=initial,
        command=command,
        resolution=resolution,
        padding=padding,
    )
    return controller.scale


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
