from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scanning_tool.gui.handlers import ACTION_HANDLERS
from scanning_tool.state.signals import ui_action

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.gui.actions import UiAction
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


def install_ui_action_handlers(
    config: ConfigSaver,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    def _receiver(sender: object, action: UiAction) -> None:
        handler = ACTION_HANDLERS.get(action.type)
        if handler is None:
            logging.debug("Unhandled UI action: %s", action.type)
            return

        handler(
            action.payload,
            config,
            scan_state,
            service_state,
            overlay_state,
            control_state,
            capture_service,
            config_service,
        )

    ui_action.connect(_receiver, weak=False)
