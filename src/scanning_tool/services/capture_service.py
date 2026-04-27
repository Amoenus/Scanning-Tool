"""Service for handling screen capture and OCR processing."""

from __future__ import annotations

import time
from threading import Thread
from typing import TYPE_CHECKING

from loguru import logger

from scanning_tool.application.capture import CaptureUseCase
from scanning_tool.interfaces import CaptureController, StatusCallback
from scanning_tool.services.alignment_adapter import UIAlignmentAdapter
from scanning_tool.services.capture_provider import ScreenCaptureProvider
from scanning_tool.services.deposit_lookup_adapter import DepositLookupAdapter
from scanning_tool.services.ocr_provider import OllamaOCRProvider

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
class CaptureService(CaptureController):
    """Service for capturing screen regions and processing OCR results."""

    def __init__(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
    ) -> None:
        self._config = config
        self._scan_state = scan_state
        self._capture_use_case = CaptureUseCase(
            config=config,
            scan_state=scan_state,
            capture_provider=ScreenCaptureProvider(),
            ocr_provider=OllamaOCRProvider(),
            deposit_lookup=DepositLookupAdapter(service_state.code_re),
            alignment_adapter=UIAlignmentAdapter(),
            code_re=service_state.code_re,
        )

    def capture_once(self, status_callback: StatusCallback | None = None) -> None:
        """Capture one scan from the capture region and update overlay."""
        self._capture_use_case.capture_once(status_callback=status_callback)

    def toggle_continuous(self) -> None:
        """Toggle continuous scanning mode."""
        enabled = not self._scan_state.continuous_mode
        self._scan_state.set_continuous_mode(enabled)
        logger.info(f"Continuous mode: {self._scan_state.continuous_mode}")

        if self._scan_state.continuous_mode:
            Thread(target=self._continuous_scan_loop, daemon=True).start()

    def _continuous_scan_loop(self) -> None:
        """Run scans repeatedly until continuous_mode is turned off."""
        while self._scan_state.continuous_mode:
            self.capture_once()
            interval = max(0.1, float(self._config.continuous_capture_interval))
            time.sleep(interval)
