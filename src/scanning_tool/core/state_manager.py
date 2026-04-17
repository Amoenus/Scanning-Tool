"""Centralized registry for strongly typed state architectures."""

from scanning_tool.state.app_state import AppState

app_state = AppState()
config = app_state.load_config()
scan_state = app_state.scan_state
service_state = app_state.service_state
overlay_state = app_state.overlay_state
control_state = app_state.control_state


def save_config() -> None:
    """Helper to save the current configuration."""
    app_state.save_config()
