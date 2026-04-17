"""Main entry point - startup orchestration."""

from threading import Thread

from loguru import logger

from scanning_tool.deposits import load_rock_data
from scanning_tool.gui.app import launch_gui
from scanning_tool.services.hotkeys_service import hotkey_listener
from scanning_tool.logging_setup import setup_logging
from scanning_tool.ollama import (
    ensure_model_installed,
    ensure_ollama_installed,
    log_model_running_status,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.ollama_service import ollama_service
from scanning_tool.state.manager import config, scan_state
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.web import create_app, get_local_ip


def _initialize_services() -> None:
    """Start core services and ensure the Ollama model is available."""
    ensure_ollama_installed()
    ollama_service.start()
    alignment_service.start()
    ensure_model_installed()
    log_model_running_status()


def _initialize_anchor_tracking() -> None:
    """Create and register the anchor region tracker."""
    scan_state.anchor_tracker = AnchorRegionTracker(
        config.anchor_template_dir,
        config.anchor_threshold,
    )


def _start_hotkey_listener() -> None:
    """Launch the global hotkey listener on a background thread."""
    Thread(target=hotkey_listener, daemon=True).start()


def _start_web_server() -> None:
    """Launch the Flask overlay server on a background thread."""
    web_config = config.web_server_config
    host = web_config.host
    port = web_config.port

    msg = f"Starting overlay server: http://127.0.0.1:{port}"
    if host == "0.0.0.0":
        local_ip = get_local_ip()
        msg += f" (this device) | http://{local_ip}:{port} (local network)"
    logger.info(msg)

    flask_app = create_app()
    Thread(
        target=lambda: flask_app.run(host=host, port=port, debug=False),
        daemon=True,
    ).start()


def main() -> None:
    """Launch the scanning tool."""
    setup_logging()
    load_rock_data()
    _initialize_services()
    _initialize_anchor_tracking()
    _start_hotkey_listener()
    _start_web_server()
    try:
        launch_gui()
    finally:
        ollama_service.stop()
        alignment_service.stop()
