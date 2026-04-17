"""Application state container for the scanning tool."""

from dataclasses import dataclass, field

from scanning_tool.services.config_service import ConfigData, ConfigService
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.gui.control_state import ControlState
from scanning_tool.gui.overlay_state import OverlayState


@dataclass
class AppState:
    """Typed container for shared runtime state."""

    config_service: ConfigService = field(default_factory=ConfigService)
    config: ConfigData = field(init=False)
    scan_state: ScanState = field(default_factory=ScanState)
    service_state: ServiceState = field(default_factory=ServiceState)
    overlay_state: OverlayState = field(default_factory=OverlayState)
    control_state: ControlState = field(default_factory=ControlState)

    def __post_init__(self) -> None:
        self.config = self.config_service.load()

    def save_config(self) -> None:
        self.config_service.save()
