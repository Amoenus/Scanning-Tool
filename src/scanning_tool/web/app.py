"""Flask web server for the mobile/browser overlay."""

from __future__ import annotations

import socket

from flask import Flask, Response, jsonify, render_template, request

from scanning_tool.config import resource_path
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.common import SpaceSystem
from scanning_tool.interfaces.web import StatusResponseBuilder
from scanning_tool.logging_setup import configure_flask_logging
from scanning_tool.state import manager
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.web.status_builder import DefaultStatusResponseBuilder

DEFAULT_SELECTED_REGION = SpaceSystem.STANTON


class WebService:
    """Expose scan state through a browser overlay and status API."""

    def __init__(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        template_folder: str,
        status_response_builder: StatusResponseBuilder,
    ) -> None:
        self.config = config
        self.scan_state = scan_state
        self.service_state = service_state
        self.template_folder = template_folder
        self._status_response_builder = status_response_builder

    @staticmethod
    def get_local_ip() -> str:
        """Best-effort detection of the primary local network IP address."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                ip_address = sock.getsockname()[0]
                if ip_address:
                    return ip_address
        except Exception:
            pass
        return "127.0.0.1"

    def _index(self) -> str:
        return render_template("overlay.html")

    def _status(self) -> Response:
        """Return the latest scan information for the overlay UI."""
        selected_region = self._selected_region()
        response = self._build_status_response(selected_region)
        return jsonify(response.to_dict())

    def _selected_region(self) -> SpaceSystem:
        requested_region = request.args.get("region", DEFAULT_SELECTED_REGION.value)
        return SpaceSystem.normalize(requested_region)

    def _build_status_response(self, selected_region: SpaceSystem):
        return self._status_response_builder.build_status_response(
            self.config,
            self.scan_state,
            self.service_state,
            selected_region,
        )

    def create_app(self) -> Flask:
        """Create and configure the Flask application."""
        app = Flask(__name__, template_folder=self.template_folder)
        configure_flask_logging(app)
        app.add_url_rule("/", endpoint="index", view_func=self._index)
        app.add_url_rule("/status", endpoint="status", view_func=self._status)
        return app


def create_app() -> Flask:
    """Create the default Flask app using global runtime state."""
    return WebService(
        config=manager.config,
        scan_state=manager.scan_state,
        service_state=manager.service_state,
        template_folder=resource_path("templates"),
        status_response_builder=DefaultStatusResponseBuilder(),
    ).create_app()


get_local_ip = WebService.get_local_ip
