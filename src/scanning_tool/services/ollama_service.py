"""Ollama lifecycle management service."""

import socket
import shutil
import subprocess
import sys
from typing import Optional

from tenacity import RetryError, retry, retry_if_result, stop_after_delay, wait_fixed

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

        if self._should_use_remote_host(host):
            return

        if self._ensure_local_ollama_running(host):
            return

        self._start_local_ollama(host)

    def _should_use_remote_host(self, host: str) -> bool:
        if not is_local_ollama_host(host):
            self.logger.info(
                f"Using remote Ollama host at {host}; assuming it is managed externally."
            )
            return True
        return False

    def _ensure_local_ollama_running(self, host: str) -> bool:
        if self._is_running(host):
            self.logger.info("Local Ollama service detected.")
            return True
        return False

    def _start_local_ollama(self, host: str) -> None:
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
        @retry(
            retry=retry_if_result(lambda running: running is False),
            wait=wait_fixed(0.5),
            stop=stop_after_delay(10.0),
            reraise=True,
        )
        def wait_until_running() -> bool:
            if (
                self._daemon_process is not None
                and self._daemon_process.poll() is not None
            ):
                raise RuntimeError(
                    "'ollama serve' exited before the service became ready."
                )
            return self._is_running(host)

        try:
            wait_until_running()
            self.logger.info("Ollama service is now running gracefully.")
        except RetryError:
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
