"""Ollama lifecycle management service."""

import socket
import shutil
import subprocess
import sys
import time
from typing import Optional

from scanning_tool.services.base_service import BaseService
from scanning_tool.ollama.host import (
    get_ollama_host,
    is_local_ollama_host,
    _get_host_port,
)


class OllamaService(BaseService):
    """Manages the Ollama process and model availability via encapsulated subprocess daemon."""

    def __init__(self):
        super().__init__()
        self._daemon_process: Optional[subprocess.Popen] = None

    def _is_running(self, host: str, timeout: float = 2.0) -> bool:
        hostname, port = _get_host_port(host)
        try:
            with socket.create_connection((hostname, port), timeout=timeout):
                return True
        except OSError:
            return False

    def _on_start(self) -> None:
        self.logger.info("Initializing Ollama backend logic...")
        host = get_ollama_host()

        if not is_local_ollama_host(host):
            self.logger.info(
                f"Using remote Ollama host at {host}; assuming it is managed externally."
            )
            return

        if self._is_running(host):
            self.logger.info("Local Ollama service detected.")
            return

        if not shutil.which("ollama"):
            self.logger.warning(
                "Cannot start Ollama automatically because it is not installed."
            )
            sys.exit(
                "Unable to reach a local Ollama service. Please start 'ollama serve' and rerun."
            )

        self._spawn_ollama_daemon()
        self._wait_for_readiness(host)

    def _spawn_ollama_daemon(self) -> None:
        self.logger.info("Starting local Ollama service with 'ollama serve'...")
        try:
            self._daemon_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as exc:
            self.logger.error(f"Unable to start Ollama service automatically: {exc}")
            sys.exit("Ollama failed to launch.")

    def _wait_for_readiness(self, host: str) -> None:
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self._is_running(host):
                self.logger.info("Ollama service is now running gracefully.")
                return
            daemon_process = self._daemon_process
            if daemon_process is not None and daemon_process.poll() is not None:
                self.logger.error(
                    "'ollama serve' exited before the service became ready."
                )
                sys.exit("Ollama exit crash.")
            time.sleep(0.5)

        self.logger.warning("Timed out waiting for Ollama service to start.")
        sys.exit("Ollama daemon timeout.")

    def _on_stop(self) -> None:
        self.logger.info("Shutting down Ollama integration.")
        if self._daemon_process and self._daemon_process.poll() is None:
            self._daemon_process.terminate()
            self._daemon_process.wait(timeout=3.0)
            self.logger.info("Ollama daemon safely terminated.")


# Provide the singleton instances here like capture_service
ollama_service = OllamaService()
