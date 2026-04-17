"""Centralized registry for strongly typed state architectures."""

from scanning_tool.services.config_service import ConfigService
from scanning_tool.state.scan_state import ScanState
from scanning_tool.runtime.service_state import ServiceState
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.gui.control_state import ControlState

config_service = ConfigService()
config = config_service.load()

scan_state = ScanState()
service_state = ServiceState()
overlay_state = OverlayState()
control_state = ControlState()


def save_config() -> None:
    """Helper to save the current configuration."""
    config_service.save()
