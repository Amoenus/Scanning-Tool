"""Control widgets for the scanning tool GUI."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Optional

GlassScaleCommand = Callable[[str], None]

GLASS_SECTION_TFRAME_STYLE = "Glass.Section.TFrame"
GLASS_SMALL_TLABEL_STYLE = "Glass.Small.TLabel"
GLASS_HORIZONTAL_TSCALE_STYLE = "Glass.Horizontal.TScale"
GLASS_TBUTTON_STYLE = "Glass.TButton"


def create_section_row(parent: ttk.Widget, pady: tuple[int, int] = (0, 5)) -> ttk.Frame:
    """Create a styled row container for section controls."""
    row = ttk.Frame(parent, style=GLASS_SECTION_TFRAME_STYLE)
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
        padding: tuple[int, int],
    ) -> None:
        self._text = text
        self._command = command
        self._resolution = resolution

        self._container = ttk.Frame(parent, style=GLASS_SECTION_TFRAME_STYLE)
        self._container.pack(fill="x", padx=4, pady=padding)

        self._value_var = tk.DoubleVar(value=initial)
        self._label_var = tk.StringVar(value=self._create_label(initial))
        ttk.Label(
            self._container,
            textvariable=self._label_var,
            style=GLASS_SMALL_TLABEL_STYLE,
        ).pack(anchor="w", padx=2)

        self._scale = ttk.Scale(
            self._container,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            variable=self._value_var,
            command=self._on_change,
            style=GLASS_HORIZONTAL_TSCALE_STYLE,
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
        return (
            round(value / self._resolution) * self._resolution
            if self._resolution
            else value
        )

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
    padding: tuple[int, int] = (0, 4),
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


class ResponsiveButtonRow(ttk.Frame):
    """A button container that switches between horizontal and vertical layouts."""

    MIN_BUTTON_WIDTH = 140

    def __init__(self, parent: ttk.Widget, style: str = GLASS_SECTION_TFRAME_STYLE) -> None:
        super().__init__(parent, style=style)
        self.pack(fill="x", padx=5, pady=(0, 5))
        self._buttons: list[ttk.Button] = []
        self._button_specs: list[
            tuple[str | tk.StringVar, Callable[[], None], str]
        ] = []
        self.bind("<Configure>", self._on_configure)

    def add_button(
        self,
        label: str | tk.StringVar,
        command: Callable[[], None],
        style: str,
    ) -> None:
        self._button_specs.append((label, command, style))
        if isinstance(label, tk.StringVar):
            button = ttk.Button(
                self,
                textvariable=label,
                command=command,
                style=style,
            )
        else:
            button = ttk.Button(self, text=label, command=command, style=style)

        self._buttons.append(button)
        button.grid(row=0, column=len(self._buttons) - 1, sticky="ew", padx=5, pady=2)
        self.columnconfigure(len(self._buttons) - 1, weight=1)
        self._apply_layout(self.winfo_width())

    def _on_configure(self, event: tk.Event) -> None:
        self._apply_layout(event.width)

    def _apply_layout(self, width: int) -> None:
        if not self._buttons:
            return

        use_stacked = width < len(self._buttons) * self.MIN_BUTTON_WIDTH
        for index, button in enumerate(self._buttons):
            button.grid_forget()
            if use_stacked:
                button.grid(row=index, column=0, sticky="ew", padx=5, pady=2)
            else:
                button.grid(row=0, column=index, sticky="ew", padx=5, pady=2)

        if use_stacked:
            self.columnconfigure(0, weight=1)
            for column in range(1, len(self._buttons)):
                self.columnconfigure(column, weight=0)
        else:
            for column in range(len(self._buttons)):
                self.columnconfigure(column, weight=1)


def create_button_row(
    parent: ttk.Widget,
    buttons: list[tuple[str | tk.StringVar, Callable[[], None]]],
    style: str = GLASS_TBUTTON_STYLE,
) -> ttk.Frame:
    """Create a responsive row of buttons."""
    row = ResponsiveButtonRow(parent)
    for label, command in buttons:
        row.add_button(label, command, style)
    return row
