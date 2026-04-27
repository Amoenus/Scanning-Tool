from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
@dataclass(frozen=True)
class GuiSectionDependencies:
    """Shared dependencies that every GUI section needs."""

    config: ConfigData
    scan_state: ScanState
    service_state: ServiceState
    overlay_state: OverlayState
    control_state: ControlState
    capture_service: CaptureController
    config_service: ConfigSaver
