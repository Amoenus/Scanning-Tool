"""Runtime state manager for the scanning tool."""

from scanning_tool.config.service import ConfigService
from scanning_tool.state.app_state import AppState

config_service = ConfigService()
config = config_service.load()
app_state = AppState(config=config)
scan_state = app_state.scan_state
service_state = app_state.service_state
overlay_state = app_state.overlay_state
control_state = app_state.control_state

__all__ = [
    "app_state",
    "config",
    "scan_state",
    "service_state",
    "overlay_state",
    "control_state",
    "save_config",
]


def save_config() -> None:
    """Persist the current configuration."""
    config_service.save()
