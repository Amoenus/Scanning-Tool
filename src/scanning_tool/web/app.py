"""Flask web server for the mobile/browser overlay."""

from __future__ import annotations

import socket
from typing import Optional

from flask import Flask, Response, jsonify, render_template, request

from scanning_tool.config import resource_path
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.models import (
    DepositInfo,
    DepositTable,
    ScanResult,
    StatusResponse,
)
from scanning_tool.logging_setup import configure_flask_logging
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState


class WebService:
    """Expose scan state through a browser overlay and status API."""

    def __init__(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        template_folder: str,
    ) -> None:
        self.config = config
        self.scan_state = scan_state
        self.service_state = service_state
        self.template_folder = template_folder

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

    def _lookup_deposit_table(
        self, info: Optional[DepositInfo], selected_region: str
    ) -> Optional[DepositTable]:
        if not info:
            return None
        deposit_key = (info.key or info.name or "").upper()
        region_tables = self.service_state.rocks.deposit_tables.get(selected_region, {})
        table = region_tables.get(deposit_key)
        category = str(info.category or "").lower()
        if not table or category not in {"rock deposits", "gems"}:
            return None
        return table

    def _build_status_response(
        self,
        result: Optional[ScanResult],
        info: Optional[DepositInfo],
        selected_region: str,
        table: Optional[DepositTable],
    ) -> StatusResponse:
        return StatusResponse(
            region=self.config.capture_region,
            label_color=self.config.overlay_config.label_color,
            last=result,
            alignment=self.scan_state.last_alignment_info,
            selected_region=selected_region,
            info=info,
            code=result.label if result else None,
            code_raw=result.code_raw if result else None,
            raw_text=result.raw_text if result else None,
            table=table,
        )

    def create_app(self) -> Flask:
        """Create and configure the Flask application."""
        app = Flask(__name__, template_folder=self.template_folder)
        configure_flask_logging(app)

        @app.route("/")
        def index() -> str:
            return render_template("overlay.html")

        @app.route("/status")
        def status() -> Response:
            """Return the latest scan information for the overlay UI."""
            selected_region = request.args.get("region", "STANTON").upper()
            result = self.scan_state.last_result
            info = result.info if result else None
            table = self._lookup_deposit_table(info, selected_region)
            response = self._build_status_response(
                result, info, selected_region, table
            )
            return jsonify(response.to_dict())

        return app


from scanning_tool.state.app_state import AppState


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
