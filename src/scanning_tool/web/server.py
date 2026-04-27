"""WSGI server startup abstraction for the web overlay."""

from __future__ import annotations

from flask import Flask
from waitress import serve


class WebServer:
    """Launch the web overlay using the configured server backend."""

    @staticmethod
    def run(app: Flask, host: str, port: int, threads: int = 6) -> None:
        serve(app, host=host, port=port, threads=threads, _quiet=True)
