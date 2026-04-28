from __future__ import annotations

import io
import logging
import os
import subprocess
import sys
import webbrowser
from threading import Thread
from typing import TYPE_CHECKING

from scanning_tool.config import ensure_anchor_directory
from scanning_tool.domain.alignment import AlignmentRequest
from scanning_tool.gui.actions import UiAction, UiActionType
from scanning_tool.gui.overlays import (
    hide_anchor_overlay,
    reposition_info_overlay,
    show_anchor_overlay,
    show_capture_overlay,
    toggle_border,
    update_anchor_overlay_region,
    update_capture_overlay_region,
)
from scanning_tool.ollama import (
    ensure_model_installed,
    get_ollama_host,
    is_local_ollama_host,
    log_model_running_status,
    set_configured_ollama_host,
    set_configured_ollama_model,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.capture_provider import ScreenCaptureProvider
from scanning_tool.state.signals import (
    mobile_qr_ready,
    status_updated,
    ui_action,
)

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


def install_ui_action_handlers(
    config,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    def _receiver(sender: object, action: UiAction) -> None:
        _dispatch_ui_action(
            action,
            config=config,
            scan_state=scan_state,
            service_state=service_state,
            overlay_state=overlay_state,
            control_state=control_state,
            capture_service=capture_service,
            config_service=config_service,
        )

    ui_action.connect(_receiver, weak=False)


def _dispatch_ui_action(
    action: UiAction,
    config,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    payload = action.payload

    if action.type == UiActionType.SINGLE_SCAN:
        Thread(target=capture_service.capture_once, daemon=True).start()
        status_updated.send(None, message="Single scan requested.")
        return

    if action.type == UiActionType.TOGGLE_CONTINUOUS_CAPTURE:
        capture_service.toggle_continuous()
        status_updated.send(None, message="Toggled continuous capture mode.")
        return

    if action.type == UiActionType.UPDATE_CONTINUOUS_CAPTURE_INTERVAL:
        value = float(payload.get("value", config.continuous_capture_interval))
        config.continuous_capture_interval = value
        status_updated.send(None, message=f"Continuous capture interval set to {value:.1f}s")
        return

    if action.type == UiActionType.SAVE_CONFIG:
        config_service.save()
        status_updated.send(None, message="Configuration saved.")
        return

    if action.type == UiActionType.OPEN_MOBILE_UI:
        url = payload["url"]
        try:
            webbrowser.open_new_tab(url)
            status_updated.send(None, message=f"Opening overlay in browser: {url}")
        except Exception as exc:
            status_updated.send(None, message=f"Unable to open browser: {exc}")
        return

    if action.type == UiActionType.SHOW_MOBILE_QR:
        url = payload.get("url", "")
        if not url:
            status_updated.send(None, message="Unable to generate mobile QR code: missing URL.")
            return

        try:
            import segno

            qr = segno.make(url, error="h")
            with io.BytesIO() as buffer:
                qr.save(buffer, kind="png", scale=8, border=2)
                png_bytes = buffer.getvalue()
        except Exception as exc:
            status_updated.send(None, message=f"Unable to generate QR code: {exc}")
            logging.exception("Failed to generate mobile QR code for %s: %s", url, exc)
            return

        mobile_qr_ready.send(None, url=url, png_bytes=png_bytes)
        status_updated.send(None, message="Mobile overlay QR code generated.")
        return

    if action.type == UiActionType.APPLY_OLLAMA_MODEL:
        model_value = payload.get("model", "").strip()
        if not model_value:
            status_updated.send(None, message="Please specify an Ollama model.")
            return
        set_configured_ollama_model(model_value)
        try:
            ensure_model_installed(model_value, exit_on_error=False)
        except Exception as exc:
            status_updated.send(None, message=f"Model install failed: {exc}")
            logging.exception("Failed to install model %s: %s", model_value, exc)
            return
        running = log_model_running_status(model_value)
        message = (
            f"Ollama model set to {model_value} and is currently running."
            if running
            else f"Ollama model set to {model_value}. It is not running yet and will start on first scan."
        )
        status_updated.send(None, message=message)
        return

    if action.type == UiActionType.APPLY_OLLAMA_HOST:
        host_value = payload.get("host", "").strip()
        normalized = set_configured_ollama_host(host_value)
        config.ollama_config.host = normalized
        active_host = get_ollama_host()
        message = (
            f"Remote Ollama host set to {active_host}."
            if normalized
            else f"Ollama host cleared. Using {active_host}."
        )
        status_updated.send(None, message=message)
        return

    if action.type == UiActionType.USE_LOCALHOST:
        set_configured_ollama_host("")
        config.ollama_config.host = ""
        active_host = get_ollama_host()
        status_updated.send(None, message=f"Ollama host cleared. Using {active_host}.")
        return

    if action.type == UiActionType.RESTART_OLLAMA:
        host = get_ollama_host()
        if not is_local_ollama_host(host):
            message = (
                "Remote Ollama host configured; local service cannot be restarted. "
                "Switch to localhost to use automatic restart."
            )
            status_updated.send(None, message=message)
            return
        status_updated.send(None, message="Restarting local Ollama service...")
        try:
            from scanning_tool.services.ollama_service import ollama_service

            if ollama_service.is_running:
                ollama_service.stop()
            ollama_service.start()
        except Exception as exc:
            status_updated.send(None, message=f"Failed to restart local Ollama service: {exc}")
            logging.exception("Failed to restart Ollama service: %s", exc)
        else:
            status_updated.send(None, message="Local Ollama service restarted successfully.")
        return

    if action.type == UiActionType.TOGGLE_AUTO_ALIGNMENT:
        enabled = bool(payload.get("enabled", False))
        config.auto_alignment.enabled = enabled
        scan_state.last_alignment_info.enabled = enabled
        scan_state.notify_alignment_info_listeners()
        status_updated.send(None, message=(
            "Head sway compensation enabled." if enabled else "Head sway compensation disabled."
        ))
        return

    if action.type == UiActionType.TOGGLE_ANCHOR_OVERLAY:
        visible = bool(payload.get("visible", False))
        overlay_state.anchor.visible = visible
        if visible:
            show_anchor_overlay(overlay_state, config.anchor_template)
            status_updated.send(None, message="Anchor overlay shown.")
        else:
            hide_anchor_overlay(overlay_state)
            status_updated.send(None, message="Anchor overlay hidden.")
        return

    if action.type == UiActionType.UPDATE_ALIGNMENT_POLL_INTERVAL:
        config.alignment_poll_interval_ms = int(payload.get("value", config.alignment_poll_interval_ms))
        status_updated.send(None, message=f"Alignment interval set to {config.alignment_poll_interval_ms} ms")
        return

    if action.type == UiActionType.UPDATE_ANCHOR_THRESHOLD:
        threshold = float(payload.get("value", config.anchor_threshold))
        config.anchor_threshold = max(0.1, min(0.99, threshold))
        if scan_state.anchor_tracker is not None:
            scan_state.anchor_tracker.set_threshold(config.anchor_threshold)
        status_updated.send(None, message=f"Anchor detection threshold set to {config.anchor_threshold:.2f}")
        return

    if action.type == UiActionType.UPDATE_ANCHOR_REGION:
        region = config.anchor_template
        region.left = int(payload.get("left", region.left))
        region.top = int(payload.get("top", region.top))
        region.width = int(payload.get("width", region.width))
        region.height = int(payload.get("height", region.height))
        status_updated.send(None, message=f"Anchor region updated: {region}")
        update_anchor_overlay_region(overlay_state)
        return

    if action.type == UiActionType.UPDATE_ANCHOR_OFFSET:
        offset = config.anchor_offset
        offset.x = int(payload.get("x", offset.x))
        offset.y = int(payload.get("y", offset.y))
        status_updated.send(None, message=f"Anchor offset updated: {offset}")
        update_anchor_overlay_region(overlay_state)
        return

    if action.type == UiActionType.RELOAD_ANCHOR_TEMPLATES:
        ensure_anchor_directory(config.anchor_template_dir)
        if scan_state.anchor_tracker is None:
            scan_state.anchor_tracker = AnchorRegionTracker(
                config.anchor_template_dir,
                ScreenCaptureProvider(),
                config.anchor_threshold,
            )
        count = scan_state.anchor_tracker.set_directory(config.anchor_template_dir)
        status_updated.send(None, message=f"Loaded {count} anchor template(s) from {config.anchor_template_dir}.")
        return

    if action.type == UiActionType.MANUAL_REALIGN:
        if _run_manual_realign(config, scan_state):
            info = scan_state.last_alignment_info
            status_updated.send(None, message=(
                f"Anchor locked using {info.template} (score {info.score:.2f})."
            ))
        else:
            status_updated.send(None, message="Anchor match not found. Adjust search region or add templates.")
        return

    if action.type == UiActionType.OPEN_ANCHOR_DIRECTORY:
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
        return

    if action.type == UiActionType.UPDATE_CAPTURE_REGION:
        region = config.capture_region
        region.left = int(payload.get("left", region.left))
        region.top = int(payload.get("top", region.top))
        region.width = int(payload.get("width", region.width))
        region.height = int(payload.get("height", region.height))
        status_updated.send(None, message=f"CAP_REGION updated: {region}")
        update_capture_overlay_region()
        return
    if action.type == UiActionType.TOGGLE_CAPTURE_BOX:
        visible = bool(payload.get("visible", False))
        if visible:
            show_capture_overlay(overlay_state, config.capture_region)
            status_updated.send(None, message="Capture box shown.")
        else:
            from scanning_tool.gui.overlays import hide_capture_overlay

            hide_capture_overlay(overlay_state)
            status_updated.send(None, message="Capture box hidden.")
        return
    if action.type == UiActionType.TOGGLE_CAPTURE_BORDER:
        toggle_border(overlay_state)
        status_updated.send(None, message=f"Capture border {'enabled' if overlay_state.show_border else 'disabled'}.")
        return

    if action.type == UiActionType.UPDATE_RESULT_DISPLAY_OFFSET:
        offset = config.overlay_config.info_offset
        offset.x = int(payload.get("x", offset.x))
        offset.y = int(payload.get("y", offset.y))
        status_updated.send(None, message=f"Display offset updated: x={offset.x}, y={offset.y}")
        reposition_info_overlay(overlay_state, config.overlay_config)
        return

    logging.debug("Unhandled UI action: %s", action.type)


def _run_manual_realign(config, scan_state: ScanState) -> bool:
    result = alignment_service.align(
        scan_state.anchor_tracker,
        scan_state.last_alignment_info,
        AlignmentRequest.from_config(config),
    )
    scan_state.notify_alignment_info_listeners()
    return result
