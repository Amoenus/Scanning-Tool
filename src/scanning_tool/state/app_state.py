"""Application state container for the scanning tool."""

from dataclasses import dataclass, field
from typing import Optional

from scanning_tool.services.config_service import ConfigData, ConfigService
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.gui.control_state import ControlState
from scanning_tool.gui.overlay_state import OverlayState


@dataclass
class AppState:
    """Typed container for shared runtime state."""

    config_service: ConfigService = field(default_factory=ConfigService)
    config: Optional[ConfigData] = field(default=None, init=False)
    scan_state: ScanState = field(default_factory=ScanState)
    service_state: ServiceState = field(default_factory=ServiceState)
    overlay_state: OverlayState = field(default_factory=OverlayState)
    control_state: ControlState = field(default_factory=ControlState)

    def load_config(self) -> ConfigData:
        """Explicitly load configuration data from disk."""
        self.config = self.config_service.load()
        return self.config

    def save_config(self) -> None:
        if self.config is None:
            raise ValueError("Configuration has not been loaded")
        self.config_service.save()
