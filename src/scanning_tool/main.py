"""Main entry point - startup orchestration."""

from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from loguru import logger

from scanning_tool.bootstrap import bootstrap
from scanning_tool.config import resource_path
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.deposits import load_rock_data
from scanning_tool.gui.provider import get_default_gui_provider
from scanning_tool.logging_setup import setup_logging
from scanning_tool.ollama import (
    ensure_model_installed,
    ensure_ollama_installed,
    log_model_running_status,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.capture_provider import ScreenCaptureProvider
from scanning_tool.services.edit_mode_service import edit_mode_service
from scanning_tool.services.hotkeys_service import hotkey_listener
from scanning_tool.services.ollama_service import ollama_service
from scanning_tool.state import manager
from scanning_tool.state.signals import (
    alignment_failed,
    alignment_requested,
    alignment_reset,
    scan_completed,
    scan_failed,
    scan_started,
    ui_action,
)
from scanning_tool.web.app import WebService
from scanning_tool.web.server import WebServer
from scanning_tool.web.status_builder import DefaultStatusResponseBuilder

if TYPE_CHECKING:
    from flask import Flask

    from scanning_tool.config.service import ConfigData
    from scanning_tool.services.capture_service import CaptureService
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


def _initialize_services() -> None:
    """Start core services and ensure the Ollama model is available."""
    ensure_ollama_installed()
    ollama_service.start()
    alignment_service.start()
    edit_mode_service.start()
    ensure_model_installed()
    log_model_running_status()


def _initialize_anchor_tracking(config: ConfigData, scan_state: ScanState) -> None:
    """Create and register the anchor region tracker."""
    scan_state.anchor_tracker = AnchorRegionTracker(
        config.anchor_template_dir,
        ScreenCaptureProvider(),
        config.anchor_threshold,
    )


def _start_hotkey_listener(capture_service: CaptureService) -> None:
    """Launch the global hotkey listener on a background thread."""
    Thread(target=lambda: hotkey_listener(capture_service), daemon=True).start()


def _start_web_server(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
) -> None:
    """Launch the Flask overlay server on a background thread.

    This function requires fully initialized runtime state. Missing state is a
    fatal startup error because the overlay server cannot operate correctly
    without the configuration and shared state objects.
    """
    web_config = config.web_server_config
    host = web_config.host
    port = web_config.port

    msg = f"Starting overlay server: http://127.0.0.1:{port}"
    if host == "0.0.0.0":
        local_ip = get_local_ip()
        msg += f" (this device) | http://{local_ip}:{port} (local network)"
    logger.info(msg)

    flask_app = _build_flask_app(config, scan_state, service_state)
    Thread(
        target=lambda: WebServer.run(
            flask_app,
            host=host,
            port=port,
            threads=web_config.threads,
        ),
        daemon=True,
    ).start()


def _on_scan_started(sender: object, **kwargs: object) -> None:
    logger.debug("Capture pipeline started.")


def _on_scan_completed(sender: object, scan_result=None, **kwargs: object) -> None:
    label = getattr(scan_result, "label", "UNKNOWN")
    logger.info("Capture completed: {}", label)


def _on_scan_failed(sender: object, error=None, **kwargs: object) -> None:
    logger.warning("Capture failed: {}", error)


def _on_alignment_requested(sender: object, alignment_request=None, **kwargs: object) -> None:
    logger.debug("Alignment requested: {}", alignment_request)


def _on_alignment_failed(sender: object, reason=None, **kwargs: object) -> None:
    logger.warning("Alignment failed: {}", reason)


def _on_alignment_reset(sender: object, **kwargs: object) -> None:
    logger.debug("Alignment reset to default state.")


def _on_ui_action(sender: object, action=None, **kwargs: object) -> None:
    logger.debug("UI action published: %s", action)


def _register_runtime_signal_handlers() -> None:
    ui_action.connect(_on_ui_action, weak=False)
    scan_started.connect(_on_scan_started, weak=False)
    scan_completed.connect(_on_scan_completed, weak=False)
    scan_failed.connect(_on_scan_failed, weak=False)
    alignment_requested.connect(_on_alignment_requested, weak=False)
    alignment_failed.connect(_on_alignment_failed, weak=False)
    alignment_reset.connect(_on_alignment_reset, weak=False)


def _build_flask_app(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
) -> Flask:
    return WebService(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        template_folder=resource_path("templates"),
        status_response_builder=DefaultStatusResponseBuilder(),
    ).create_app()


def create_app() -> Flask:
    """Create the default Flask app using global runtime state."""
    return _build_flask_app(
        config=manager.config,
        scan_state=manager.scan_state,
        service_state=manager.service_state,
    )


def get_local_ip() -> str:
    return WebService.get_local_ip()


def _create_capture_service(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
) -> CaptureService:
    from scanning_tool.services.capture_service import CaptureService

    return CaptureService(config, scan_state, service_state)


def _launch_gui(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
    capture_service: CaptureService,
) -> None:
    gui_provider = get_default_gui_provider(config)
    gui_provider.launch_gui(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        overlay_state=manager.overlay_state,
        control_state=manager.control_state,
        capture_service=capture_service,
        config_service=manager.config_service,
    )


def _shutdown_services() -> None:
    ollama_service.stop()
    alignment_service.stop()
    edit_mode_service.stop()


def main() -> None:
    """Launch the scanning tool."""
    setup_logging()

    app_state = bootstrap()
    config = app_state.config
    scan_state = app_state.scan_state
    service_state = app_state.service_state
    load_rock_data(service_state)

    capture_service = _create_capture_service(config, scan_state, service_state)

    _register_runtime_signal_handlers()
    _initialize_services()
    _initialize_anchor_tracking(config, scan_state)
    _start_hotkey_listener(capture_service)
    _start_web_server(config, scan_state, service_state)

    try:
        _launch_gui(config, scan_state, service_state, capture_service)
    finally:
        _shutdown_services()
