from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING

from scanning_tool.gui.handlers import ACTION_HANDLERS
from scanning_tool.state.signals import UI_ACTION_SIGNALS
from scanning_tool.gui.action_context import ActionContext

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
    """Connect UI action handlers to their corresponding UI action signals.

    Parameters
    ----------
    config : ConfigData
        The configuration data object.
    scan_state : ScanState
        The scan state object.
    service_state : ServiceState
        The service state object.
    overlay_state : OverlayState
        The overlay state object.
    control_state : ControlState
        The control state object.
    capture_service : CaptureController
        The capture controller/service.
    config_service : ConfigSaver
        The configuration saver/service.

    """
    context = ActionContext(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        overlay_state=overlay_state,
        control_state=control_state,
        capture_service=capture_service,
        config_service=config_service,
    )

    def _receiver(
        handler,
        sender: object,
        payload: dict[str, object] | None = None,
    ) -> None:
        try:
            handler(payload or {}, context)
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
