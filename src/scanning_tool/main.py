"""Main entry point - startup orchestration."""

from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from flask import Flask
from loguru import logger

from scanning_tool.config import resource_path
from scanning_tool.deposits import load_rock_data
from scanning_tool.logging_setup import setup_logging
from scanning_tool.ollama import (
    ensure_model_installed,
    ensure_ollama_installed,
    log_model_running_status,
)

if TYPE_CHECKING:
    from scanning_tool.services.capture_service import CaptureService


def _initialize_services() -> None:
    """Start core services and ensure the Ollama model is available."""
    from scanning_tool.services.alignment_service import alignment_service
    from scanning_tool.services.ollama_service import ollama_service

    ensure_ollama_installed()
    ollama_service.start()
    alignment_service.start()
    ensure_model_installed()
    log_model_running_status()


def _initialize_anchor_tracking(config, scan_state) -> None:
    """Create and register the anchor region tracker."""
    from scanning_tool.core.anchor import AnchorRegionTracker

    scan_state.anchor_tracker = AnchorRegionTracker(
        config.anchor_template_dir,
        config.anchor_threshold,
    )


def _start_hotkey_listener(capture_service: 'CaptureService') -> None:
    """Launch the global hotkey listener on a background thread."""
    from scanning_tool.services.hotkeys_service import hotkey_listener

    Thread(target=lambda: hotkey_listener(capture_service), daemon=True).start()


def _start_web_server(
    config=None,
    scan_state=None,
    service_state=None,
) -> None:
    """Launch the Flask overlay server on a background thread."""
    should_use_create_app = config is None or scan_state is None or service_state is None

    if should_use_create_app:
        from importlib import import_module

        runtime_state_manager = import_module("scanning_tool.state.manager")
        config = config or runtime_state_manager.config
        scan_state = scan_state or runtime_state_manager.scan_state
        service_state = service_state or runtime_state_manager.service_state

    web_config = config.web_server_config
    host = web_config.host
    port = web_config.port

    msg = f"Starting overlay server: http://127.0.0.1:{port}"
    if host == "0.0.0.0":
        local_ip = get_local_ip()
        msg += f" (this device) | http://{local_ip}:{port} (local network)"
    logger.info(msg)

    if should_use_create_app:
        flask_app = create_app()
    else:
        from scanning_tool.web.app import WebService

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
    from scanning_tool.state.app_state import AppState
    from scanning_tool.web.app import WebService

    app_state = AppState()
    config = app_state.load_config()
    return WebService(
        config=config,
        scan_state=app_state.scan_state,
        service_state=app_state.service_state,
        template_folder=resource_path("templates"),
    ).create_app()


def get_local_ip() -> str:
    from scanning_tool.web.app import WebService

    return WebService.get_local_ip()


def main() -> None:
    """Launch the scanning tool."""
    setup_logging()
    load_rock_data()

    from scanning_tool.state.app_state import AppState

    app_state = AppState()
    config = app_state.load_config()
    scan_state = app_state.scan_state
    service_state = app_state.service_state

    from scanning_tool.services.capture_service import CaptureService

    capture_service = CaptureService(config, scan_state)

    _initialize_services()
    _initialize_anchor_tracking(config, scan_state)
    _start_hotkey_listener(capture_service)
    _start_web_server(config, scan_state, service_state)

    try:
        from scanning_tool.gui.app import launch_gui

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
        from scanning_tool.services.alignment_service import alignment_service
        from scanning_tool.services.ollama_service import ollama_service

        ollama_service.stop()
        alignment_service.stop()
