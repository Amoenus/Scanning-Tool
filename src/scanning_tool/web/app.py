"""Flask web server for the mobile/browser overlay."""

from __future__ import annotations

import json
import queue
import socket
from pathlib import Path
from typing import TYPE_CHECKING

from flask import Flask, Response, jsonify, render_template, request, send_from_directory, stream_with_context
from loguru import logger

from scanning_tool.config import resource_path
from scanning_tool.domain.common import SpaceSystem
from scanning_tool.logging_setup import configure_flask_logging
from scanning_tool.state import manager
from scanning_tool.state.signals import (
    alignment_info_updated,
    continuous_mode_changed,
    scan_result_updated,
    status_updated,
)
from scanning_tool.web.status_builder import DefaultStatusResponseBuilder

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData
    from scanning_tool.interfaces.web import StatusResponseBuilder
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
    from scanning_tool.web.schemas.types import StatusResponse

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
        except OSError:
            logger.opt(exception=True).debug(
                "Unable to detect local IP address, falling back to 127.0.0.1",
            )
        return "127.0.0.1"

    def _index(self) -> str:
        return render_template(
            "overlay.html",
            region_options=[region.value for region in SpaceSystem],
            default_region=DEFAULT_SELECTED_REGION.value,
        )

    def _status(self) -> Response:
        """Return the latest scan information for the overlay UI."""
        selected_region = self._selected_region()
        response = self._build_status_response(selected_region)
        flask_response = jsonify(response.to_dict())
        flask_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return flask_response

    def _health(self) -> Response:
        return jsonify({"status": "ok"})

    def _events(self) -> Response:
        selected_region = self._selected_region()
        return Response(
            stream_with_context(self._stream_status_events(selected_region)),
            content_type="text/event-stream",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "X-Accel-Buffering": "no",
            },
        )

    def _stream_status_events(self, selected_region: SpaceSystem):
        message_queue: queue.Queue[tuple[str, str]] = queue.Queue()

        def queue_event(event_name: str, data: object) -> None:
            message_queue.put((event_name, json.dumps(data)))

        def send_current_status() -> None:
            payload = self._build_status_response(selected_region).to_dict()
            queue_event("status", payload)

        def on_scan_result(sender: object, scan_result: object | None = None) -> None:
            send_current_status()

        def on_alignment_info(sender: object, alignment_info: object) -> None:
            send_current_status()

        def on_status_updated(sender: object, message: str) -> None:
            queue_event("status_message", {"message": message})

        def on_continuous_mode(sender: object, continuous_mode: bool) -> None:
            queue_event("continuous_mode", {"enabled": continuous_mode})

        scan_receiver = scan_result_updated.connect(
            on_scan_result,
            weak=False,
        )
        alignment_receiver = alignment_info_updated.connect(
            on_alignment_info,
            weak=False,
        )
        status_receiver = status_updated.connect(on_status_updated, weak=False)
        continuous_receiver = continuous_mode_changed.connect(
            on_continuous_mode,
            weak=False,
        )

        send_current_status()

        try:
            while True:
                try:
                    event_name, message = message_queue.get(timeout=15)
                    yield f"event: {event_name}\ndata: {message}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            scan_result_updated.disconnect(scan_receiver)
            alignment_info_updated.disconnect(alignment_receiver)
            status_updated.disconnect(status_receiver)
            continuous_mode_changed.disconnect(continuous_receiver)

    def _manifest(self) -> Response:
        return send_from_directory(
            str(Path(__file__).resolve().parent / "static"),
            "manifest.json",
            mimetype="application/manifest+json",
        )

    def _service_worker(self) -> Response:
        return send_from_directory(
            str(Path(__file__).resolve().parent / "static"),
            "service-worker.js",
            mimetype="application/javascript",
        )

    def _selected_region(self) -> SpaceSystem:
        requested_region = request.args.get("region", DEFAULT_SELECTED_REGION.value)
        return SpaceSystem.normalize(requested_region)

    def _build_status_response(self, selected_region: SpaceSystem) -> StatusResponse:
        return self._status_response_builder.build_status_response(
            self.config,
            self.scan_state,
            self.service_state,
            selected_region,
        )

    def create_app(self) -> Flask:
        """Create and configure the Flask application."""
        app = Flask(
            __name__,
            template_folder=self.template_folder,
            static_folder=str(Path(__file__).resolve().parent / "static"),
            static_url_path="/static",
        )
        configure_flask_logging(app)
        app.add_url_rule("/", endpoint="index", view_func=self._index)
        app.add_url_rule("/status", endpoint="status", view_func=self._status)
        app.add_url_rule("/health", endpoint="health", view_func=self._health)
        app.add_url_rule("/events", endpoint="events", view_func=self._events)
        app.add_url_rule("/manifest.json", endpoint="manifest", view_func=self._manifest)
        app.add_url_rule("/service-worker.js", endpoint="service_worker", view_func=self._service_worker)
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
