"""Application state container for the scanning tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from scanning_tool.config.service import ConfigData
from scanning_tool.state.service_state import ServiceState
from scanning_tool.gui.control_state import ControlState
from scanning_tool.gui.overlay_state import OverlayState

if TYPE_CHECKING:
    from scanning_tool.state.scan_state import ScanState


def _create_scan_state() -> "ScanState":
    from scanning_tool.state.scan_state import ScanState

    return ScanState()


@dataclass
class AppState:
    """Typed container for shared runtime state."""

    config: ConfigData
    scan_state: "ScanState" = field(default_factory=_create_scan_state)
    service_state: ServiceState = field(default_factory=ServiceState)
    overlay_state: OverlayState = field(default_factory=OverlayState)
    control_state: ControlState = field(default_factory=ControlState)

