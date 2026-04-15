"""Main entry point - startup orchestration."""

from loguru import logger
from threading import Thread

from threading import Thread

from scanning_tool.config import load_config
from scanning_tool.deposits import load_rock_data
from scanning_tool.gui.app import launch_gui
from scanning_tool.hotkeys import hotkey_listener
from scanning_tool.logging_setup import setup_logging
from scanning_tool.ollama import (
    ensure_model_installed,
    ensure_ollama_installed,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.ollama_service import ollama_service
from scanning_tool.state.context import app_state
from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.web import create_app, get_local_ip


def main() -> None:
    """Launch the scanning tool."""
    setup_logging()

    load_config(app_state)
    load_rock_data()

    ensure_ollama_installed()
    ollama_service.start()
    alignment_service.start()
    ensure_model_installed()
    log_model_running_status()

    app_state.scan_state.anchor_tracker = AnchorRegionTracker(
        app_state.settings.anchor.anchor_template_dir,
        app_state.settings.anchor.anchor_threshold,
    )

    Thread(target=hotkey_listener, daemon=True).start()

    local_ip = get_local_ip()
    logger.info(
        "Starting overlay server: http://127.0.0.1:5000 (this device) | "
        f"http://{local_ip}:5000 (local network)"
    )

    flask_app = create_app()
    Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=5000, debug=False),
        daemon=True,
    ).start()

    try:
        launch_gui()
    finally:
        ollama_service.stop()
        alignment_service.stop()
