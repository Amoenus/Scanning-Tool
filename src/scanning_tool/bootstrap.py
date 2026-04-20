"""Application bootstrap and dependency composition."""

from __future__ import annotations

from typing import Optional

from scanning_tool.config.service import ConfigService
from scanning_tool.state.app_state import AppState
from scanning_tool.state.manager import initialize_state


def bootstrap(config_service: Optional[ConfigService] = None) -> AppState:
    """Load configuration and initialize shared runtime state."""
    config_service = config_service or ConfigService()
    config = config_service.load()
    app_state = AppState(config=config)
    initialize_state(app_state, config_service)
    return app_state
