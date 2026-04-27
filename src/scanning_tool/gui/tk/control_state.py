from __future__ import annotations

from typing import Union

import tkinter as tk
from tkinter import ttk

from scanning_tool.gui.state import ControlState

ScaleWidget = Union[tk.Scale, ttk.Scale]

__all__ = ["ControlState", "ScaleWidget"]
