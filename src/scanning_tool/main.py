"""Main entry point - startup orchestration."""

from threading import Thread

from flask import Flask
from loguru import logger

from scanning_tool.config import resource_path
from scanning_tool.deposits import load_rock_data
from scanning_tool.gui.app import launch_gui
from scanning_tool.services.capture_service import CaptureService
from scanning_tool.services.hotkeys_service import hotkey_listener
from scanning_tool.logging_setup import setup_logging
from scanning_tool.ollama import (
    ensure_model_installed,
    ensure_ollama_installed,
    log_model_running_status,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.ollama_service import ollama_service
from scanning_tool.state.app_state import AppState
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.web.app import WebService


def _initialize_services() -> None:
    """Start core services and ensure the Ollama model is available."""
    ensure_ollama_installed()
    ollama_service.start()
    alignment_service.start()
    ensure_model_installed()
    log_model_running_status()


def _initialize_anchor_tracking(config, scan_state) -> None:
    """Create and register the anchor region tracker."""
    scan_state.anchor_tracker = AnchorRegionTracker(
        config.anchor_template_dir,
        config.anchor_threshold,
    )


def _start_hotkey_listener(capture_service: CaptureService) -> None:
    """Launch the global hotkey listener on a background thread."""
    Thread(target=lambda: hotkey_listener(capture_service), daemon=True).start()


def _start_web_server(
    config=None,
    scan_state=None,
    service_state=None,
) -> None:
    """Launch the Flask overlay server on a background thread."""
    if config is None or scan_state is None or service_state is None:
        from scanning_tool.state.app_state import AppState

        app_state = AppState()
        config = app_state.load_config()
        scan_state = app_state.scan_state
        service_state = app_state.service_state

    web_config = config.web_server_config
    host = web_config.host
    port = web_config.port

    msg = f"Starting overlay server: http://127.0.0.1:{port}"
    if host == "0.0.0.0":
        local_ip = get_local_ip()
        msg += f" (this device) | http://{local_ip}:{port} (local network)"
    logger.info(msg)

    flask_app = WebService(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        template_folder=resource_path("templates"),
    ).create_app()
    Thread(
        target=lambda: flask_app.run(host=host, port=port, debug=False),
        daemon=True,
    ).start()


def create_app() -> Flask:
    """Create the default Flask app using global runtime state."""
    app_state = AppState()
    config = app_state.load_config()
    return WebService(
        config=config,
        scan_state=app_state.scan_state,
        service_state=app_state.service_state,
        template_folder=resource_path("templates"),
    ).create_app()


get_local_ip = WebService.get_local_ip


def main() -> None:
    """Launch the scanning tool."""
    setup_logging()
    load_rock_data()

    app_state = AppState()
    config = app_state.load_config()
    scan_state = app_state.scan_state
    service_state = app_state.service_state

    capture_service = CaptureService(config, scan_state)

    _initialize_services()
    _initialize_anchor_tracking(config, scan_state)
    _start_hotkey_listener(capture_service)
    _start_web_server(config, scan_state, service_state)

    try:
        launch_gui(
            config=config,
            scan_state=scan_state,
            service_state=service_state,
            overlay_state=app_state.overlay_state,
            control_state=app_state.control_state,
            capture_service=capture_service,
            save_config=app_state.save_config,
        )
    finally:
        ollama_service.stop()
        alignment_service.stop()
