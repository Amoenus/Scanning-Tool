from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from scanning_tool.gui.dtos import ValueUpdatePayload
from scanning_tool.gui.overlays import choose_label_color, update_overlay_region
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.scan import ScanAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from collections.abc import Callable

    from scanning_tool.gui.action_context import ActionContext


def _handle_single_scan(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    Thread(target=context.capture_service.capture_once, daemon=True).start()
    status_updated.send(None, message="Single scan requested.")


def _handle_toggle_continuous_capture(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    context.capture_service.toggle_continuous()
    status_updated.send(None, message="Toggled continuous capture mode.")


def _handle_update_continuous_capture_interval(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = ValueUpdatePayload.model_validate(payload)
    if data.value is not None:
        context.config.continuous_capture_interval = float(data.value)
    status_updated.send(
        None, message=f"Continuous capture interval set to {context.config.continuous_capture_interval:.1f}s",
    )


def _handle_save_config(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    context.config_service.save()
    status_updated.send(None, message="Configuration saved.")


def _handle_update_overlay_region(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    update_overlay_region(context.overlay_state)
    status_updated.send(None, message="Overlay region refreshed.")


def _handle_choose_label_color(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    choose_label_color(context.config.overlay_config)
    status_updated.send(None, message="Label color chooser opened.")


CONTROL_ACTION_HANDLERS: dict[
    object,
    Callable[[dict[str, object], ActionContext], None],
] = {
    ScanAction.SINGLE_SCAN: _handle_single_scan,
    ScanAction.TOGGLE_CONTINUOUS_CAPTURE: _handle_toggle_continuous_capture,
    ConfigAction.UPDATE_CONTINUOUS_CAPTURE_INTERVAL: _handle_update_continuous_capture_interval,
    ConfigAction.SAVE_CONFIG: _handle_save_config,
    ConfigAction.UPDATE_OVERLAY_REGION: _handle_update_overlay_region,
    ConfigAction.CHOOSE_LABEL_COLOR: _handle_choose_label_color,
}
