from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING

from scanning_tool.gui.handlers import ACTION_HANDLERS
from scanning_tool.state.signals import UI_ACTION_SIGNALS

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


def install_ui_action_handlers(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    def _receiver(
        handler,
        sender: object,
        payload: dict[str, object] | None = None,
    ) -> None:
        try:
            handler(
                payload or {},
                config,
                scan_state,
                service_state,
                overlay_state,
                control_state,
                capture_service,
                config_service,
            )
        except Exception as exc:
            logging.exception(
                "Error handling UI action %s: %s",
                handler.__name__,
                exc,
            )

    for action_type, handler in ACTION_HANDLERS.items():
        signal = UI_ACTION_SIGNALS.get(action_type)
        if signal is None:
            logging.debug("No signal registered for UI action type: %s", action_type)
            continue

        signal.connect(partial(_receiver, handler), weak=False)
