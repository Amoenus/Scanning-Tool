"""Flask web server for the mobile/browser overlay."""

from loguru import logger
import socket
from typing import Optional

from flask import Flask, jsonify, render_template, request

from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config
from scanning_tool.config import resource_path
from scanning_tool.domain.models import DepositInfo, DepositTable, ScanResult, StatusResponse



def get_local_ip() -> str:
    """Best-effort detection of the primary local network IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip_address = sock.getsockname()[0]
            if ip_address:
                return ip_address
    except Exception as exc:
        logger.debug(f"Unable to determine local IP automatically: {exc}")
    return "127.0.0.1"


def _lookup_deposit_table(info: Optional[DepositInfo], selected_region: str) -> Optional[DepositTable]:
    if not info:
        return None
    deposit_key = (info.key or info.name or "").upper()
    region_tables = service_state.rocks.deposit_tables.get(selected_region, {})
    table = region_tables.get(deposit_key)
    category = str(info.category or "").lower()
    if not table or category not in {"rock deposits", "gems"}:
        return None
    return table


def _build_status_response(
    result: Optional[ScanResult],
    info: Optional[DepositInfo],
    selected_region: str,
    table: Optional[DepositTable],
) -> StatusResponse:
    return StatusResponse(
        region=config.capture_region,
        label_color=config.overlay_config.label_color,
        last=result,
        alignment=scan_state.last_alignment_info,
        selected_region=selected_region,
        info=info,
        code=result.label if result else None,
        code_raw=result.code_raw if result else None,
        confidence=float(result.confidence) if result and result.confidence is not None else None,
        raw_text=result.raw_text if result else None,
        table=table,
    )


def create_app() -> Flask:
    """Create and configure the Flask application."""
    template_folder = resource_path("templates")
    app = Flask(__name__, template_folder=template_folder)

    @app.route("/")
    def index():
        return render_template("overlay.html")

    @app.route("/status")
    def status():
        """Return the latest scan information for the overlay UI."""
        selected_region = request.args.get("region", "STANTON").upper()
        result = scan_state.last_result
        info = result.info if result else None
        table = _lookup_deposit_table(info, selected_region)
        response = _build_status_response(result, info, selected_region, table)
        return jsonify(response.to_dict())

    return app
