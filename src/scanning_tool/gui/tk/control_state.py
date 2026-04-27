from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Union

from scanning_tool.gui.state import ControlState

ScaleWidget = Union[tk.Scale, ttk.Scale]

__all__ = ["ControlState", "ScaleWidget"]
