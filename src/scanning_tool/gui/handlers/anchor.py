from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from scanning_tool.config import ensure_anchor_directory
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.alignment import AlignmentRequest
from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.overlays import (
    hide_anchor_overlay,
    show_anchor_overlay,
    update_anchor_overlay_region,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.capture_provider import ScreenCaptureProvider
from scanning_tool.state.signals import status_updated

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.interfaces import CaptureController


def _handle_toggle_auto_alignment(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    enabled = bool(payload.get("enabled", False))
    config.auto_alignment.enabled = enabled
    scan_state.last_alignment_info.enabled = enabled
    scan_state.notify_alignment_info_listeners()
    status_updated.send(
        None,
        message=(
            "Head sway compensation enabled." if enabled else "Head sway compensation disabled."
        ),
    )


def _handle_toggle_anchor_overlay(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    visible = bool(payload.get("visible", False))
    overlay_state.anchor_overlay_visible = visible
    if visible:
        show_anchor_overlay(overlay_state, config.anchor_template)
        status_updated.send(None, message="Anchor overlay shown.")
    else:
        hide_anchor_overlay(overlay_state)
        status_updated.send(None, message="Anchor overlay hidden.")


def _handle_update_alignment_poll_interval(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    config.alignment_poll_interval_ms = int(
        payload.get("value", config.alignment_poll_interval_ms),
    )
    status_updated.send(
        None,
        message=f"Alignment interval set to {config.alignment_poll_interval_ms} ms",
    )


def _handle_update_anchor_threshold(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    threshold = float(payload.get("value", config.anchor_threshold))
    config.anchor_threshold = max(0.1, min(0.99, threshold))
    if scan_state.anchor_tracker is not None:
        scan_state.anchor_tracker.set_threshold(config.anchor_threshold)
    status_updated.send(
        None,
        message=f"Anchor detection threshold set to {config.anchor_threshold:.2f}",
    )


def _handle_update_anchor_region(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    region = config.anchor_template
    region.left = int(payload.get("left", region.left))
    region.top = int(payload.get("top", region.top))
    region.width = int(payload.get("width", region.width))
    region.height = int(payload.get("height", region.height))
    status_updated.send(None, message=f"Anchor region updated: {region}")
    update_anchor_overlay_region(overlay_state)


def _handle_update_anchor_offset(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    offset = config.anchor_offset
    offset.x = int(payload.get("x", offset.x))
    offset.y = int(payload.get("y", offset.y))
    status_updated.send(None, message=f"Anchor offset updated: {offset}")
    update_anchor_overlay_region(overlay_state)


def _handle_reload_anchor_templates(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    ensure_anchor_directory(config.anchor_template_dir)
    if scan_state.anchor_tracker is None:
        scan_state.anchor_tracker = AnchorRegionTracker(
            config.anchor_template_dir,
            ScreenCaptureProvider(),
            config.anchor_threshold,
        )
    count = scan_state.anchor_tracker.set_directory(config.anchor_template_dir)
    status_updated.send(
        None,
        message=f"Loaded {count} anchor template(s) from {config.anchor_template_dir}.",
    )


def _run_manual_realign(config, scan_state):
    result = alignment_service.align(
        scan_state.anchor_tracker,
        scan_state.last_alignment_info,
        AlignmentRequest.from_config(config),
    )
    scan_state.notify_alignment_info_listeners()
    return result


def _handle_manual_realign(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    if _run_manual_realign(config, scan_state):
        info = scan_state.last_alignment_info
        status_updated.send(
            None,
            message=(
                f"Anchor locked using {info.template} (score {info.score:.2f})."
            ),
        )
    else:
        status_updated.send(
            None,
            message="Anchor match not found. Adjust search region or add templates.",
        )


def _handle_open_anchor_directory(
    payload: dict[str, object],
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    path = config.anchor_template_dir
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
    UiActionType.TOGGLE_AUTO_ALIGNMENT: _handle_toggle_auto_alignment,
    UiActionType.TOGGLE_ANCHOR_OVERLAY: _handle_toggle_anchor_overlay,
    UiActionType.UPDATE_ALIGNMENT_POLL_INTERVAL: _handle_update_alignment_poll_interval,
    UiActionType.UPDATE_ANCHOR_THRESHOLD: _handle_update_anchor_threshold,
    UiActionType.UPDATE_ANCHOR_REGION: _handle_update_anchor_region,
    UiActionType.UPDATE_ANCHOR_OFFSET: _handle_update_anchor_offset,
    UiActionType.RELOAD_ANCHOR_TEMPLATES: _handle_reload_anchor_templates,
    UiActionType.MANUAL_REALIGN: _handle_manual_realign,
    UiActionType.OPEN_ANCHOR_DIRECTORY: _handle_open_anchor_directory,
}
