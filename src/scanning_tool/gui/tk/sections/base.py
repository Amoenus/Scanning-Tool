"""Common types for GUI sections."""

from dataclasses import dataclass
from typing import Protocol

import tkinter as tk
from tkinter import ttk

from scanning_tool.config.service import ConfigData, ConfigSaver
from ..control_state import ControlState
from ..overlay_state import OverlayState
from ..status import StatusBar
from ..theme import GlassPalette
from scanning_tool.interfaces import CaptureController
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState


@dataclass(frozen=True)
class SectionContext:
    """Shared dependencies every section needs.

    Passed to each section's ``build`` method instead of closure-captured
    globals. Keeps sections loosely coupled to the rest of the app —
    they depend on these typed handles rather than on each other.
    """

    root: tk.Tk
    colors: GlassPalette
    status: StatusBar
    config: ConfigData
    scan_state: ScanState
    service_state: ServiceState
    overlay_state: OverlayState
    control_state: ControlState
    capture_service: CaptureController
    config_service: ConfigSaver


class Section(Protocol):
    """A UI section — one LabelFrame, self-contained widgets and callbacks."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.Frame: ...
