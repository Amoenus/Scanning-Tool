from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from scanning_tool.config import ensure_anchor_directory
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentRequest
from scanning_tool.gui.dtos import (
    OffsetUpdatePayload,
    RegionUpdatePayload,
    TogglePayload,
    ValueUpdatePayload,
)
from scanning_tool.gui.overlays import (
    hide_anchor_overlay,
    show_anchor_overlay,
    update_anchor_overlay_region,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.capture_provider import ScreenCaptureProvider
from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.actions.runtime import RuntimeAction
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.action_context import ActionContext

    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.interfaces import CaptureController


def _handle_toggle_auto_alignment(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = TogglePayload.model_validate(payload)
    enabled = bool(data.enabled)
    context.config.auto_alignment.enabled = enabled
    context.scan_state.last_alignment_info.enabled = enabled
    context.scan_state.notify_alignment_info_listeners()
    status_updated.send(
        None,
        message=("Head sway compensation enabled." if enabled else "Head sway compensation disabled."),
    )


def _handle_toggle_anchor_overlay(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = TogglePayload.model_validate(payload)
    visible = bool(data.visible)
    context.overlay_state.anchor_overlay_visible = visible
    if visible:
        show_anchor_overlay(context.overlay_state, context.config.anchor_template)
        status_updated.send(None, message="Anchor overlay shown.")
    else:
        hide_anchor_overlay(context.overlay_state)
        status_updated.send(None, message="Anchor overlay hidden.")


def _handle_update_alignment_poll_interval(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = ValueUpdatePayload.model_validate(payload)
    if data.value is not None:
        context.config.alignment_poll_interval_ms = int(data.value)
    status_updated.send(
        None,
        message=f"Alignment interval set to {context.config.alignment_poll_interval_ms} ms",
    )


def _handle_update_anchor_threshold(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = ValueUpdatePayload.model_validate(payload)
    if data.value is not None:
        threshold = float(data.value)
        context.config.anchor_threshold = max(0.1, min(0.99, threshold))
    if context.scan_state.anchor_tracker is not None:
        context.scan_state.anchor_tracker.set_threshold(context.config.anchor_threshold)
    status_updated.send(
        None,
        message=f"Anchor detection threshold set to {context.config.anchor_threshold:.2f}",
    )


def _handle_update_anchor_region(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = RegionUpdatePayload.model_validate(payload)
    region = context.config.anchor_template
    if data.left is not None:
        region.left = data.left
    if data.top is not None:
        region.top = data.top
    if data.width is not None:
        region.width = data.width
    if data.height is not None:
        region.height = data.height
    status_updated.send(None, message=f"Anchor region updated: {region}")
    update_anchor_overlay_region(context.overlay_state)


def _handle_update_anchor_offset(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    data = OffsetUpdatePayload.model_validate(payload)
    offset = context.config.anchor_offset
    if data.x is not None:
        offset.x = data.x
    if data.y is not None:
        offset.y = data.y
    status_updated.send(None, message=f"Anchor offset updated: {offset}")
    update_anchor_overlay_region(context.overlay_state)


def _handle_reload_anchor_templates(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    ensure_anchor_directory(context.config.anchor_template_dir)
    if context.scan_state.anchor_tracker is None:
        context.scan_state.anchor_tracker = AnchorRegionTracker(
            context.config.anchor_template_dir,
            ScreenCaptureProvider(),
            context.config.anchor_threshold,
        )
    count = context.scan_state.anchor_tracker.set_directory(context.config.anchor_template_dir)
    status_updated.send(
        None,
        message=f"Loaded {count} anchor template(s) from {context.config.anchor_template_dir}.",
    )


def _run_manual_realign(context: ActionContext):
    result = alignment_service.align(
        context.scan_state.anchor_tracker,
        context.scan_state.last_alignment_info,
        AlignmentRequest.from_config(context.config),
    )
    context.scan_state.notify_alignment_info_listeners()
    return result


def _handle_manual_realign(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    if _run_manual_realign(context):
        info = context.scan_state.last_alignment_info
        status_updated.send(
            None,
            message=(f"Anchor locked using {info.template} (score {info.score:.2f})."),
        )
    else:
        status_updated.send(
            None,
            message="Anchor match not found. Adjust search region or add templates.",
        )


def _handle_open_anchor_directory(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    path = context.config.anchor_template_dir
    ensure_anchor_directory(path)
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        status_updated.send(None, message=f"Opened template folder: {path}")
    except Exception as exc:
        status_updated.send(None, message=f"Unable to open template folder: {exc}")


ANCHOR_ACTION_HANDLERS = {
    ConfigAction.TOGGLE_AUTO_ALIGNMENT: _handle_toggle_auto_alignment,
    ConfigAction.TOGGLE_ANCHOR_OVERLAY: _handle_toggle_anchor_overlay,
    ConfigAction.UPDATE_ALIGNMENT_POLL_INTERVAL: _handle_update_alignment_poll_interval,
    ConfigAction.UPDATE_ANCHOR_THRESHOLD: _handle_update_anchor_threshold,
    ConfigAction.UPDATE_ANCHOR_REGION: _handle_update_anchor_region,
    ConfigAction.UPDATE_ANCHOR_OFFSET: _handle_update_anchor_offset,
    ConfigAction.RELOAD_ANCHOR_TEMPLATES: _handle_reload_anchor_templates,
    RuntimeAction.MANUAL_REALIGN: _handle_manual_realign,
    ConfigAction.OPEN_ANCHOR_DIRECTORY: _handle_open_anchor_directory,
}
