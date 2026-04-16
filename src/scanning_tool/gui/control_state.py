from dataclasses import dataclass, field
from typing import Optional, Union

import tkinter as tk
from tkinter import ttk

ScaleWidget = Union[tk.Scale, ttk.Scale]


@dataclass
class CaptureSliders:
    """Slider widgets for the capture region controls."""
    left: Optional[ScaleWidget] = None
    top: Optional[ScaleWidget] = None
    width: Optional[ScaleWidget] = None
    height: Optional[ScaleWidget] = None


@dataclass
class AnchorSliders:
    """Slider widgets for the anchor region and offset controls."""
    left: Optional[ScaleWidget] = None
    top: Optional[ScaleWidget] = None
    width: Optional[ScaleWidget] = None
    height: Optional[ScaleWidget] = None
    offset_x: Optional[ScaleWidget] = None
    offset_y: Optional[ScaleWidget] = None


@dataclass
class OverlaySliders:
    """Slider widgets for the info overlay offset controls."""
    offset_x: Optional[ScaleWidget] = None
    offset_y: Optional[ScaleWidget] = None


@dataclass
class SyncFlags:
    """Prevents re-entrant slider updates during programmatic changes."""
    capture: bool = False
    anchor: bool = False
    overlay: bool = False


@dataclass
class ControlState:
    """Typed registry for GUI slider widgets and sync guards."""
    capture: CaptureSliders = field(default_factory=CaptureSliders)
    anchor: AnchorSliders = field(default_factory=AnchorSliders)
    overlay: OverlaySliders = field(default_factory=OverlaySliders)
    syncing: SyncFlags = field(default_factory=SyncFlags)
