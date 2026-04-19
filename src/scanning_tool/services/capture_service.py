"""Service for handling screen capture and OCR processing."""

from __future__ import annotations

import time
from threading import Thread
from typing import Optional, cast

import mss
from loguru import logger
from PIL import Image

from scanning_tool.application.capture import CaptureUseCase
from scanning_tool.config.service import ConfigData
from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.domain.capture import DepositInfo
from scanning_tool.interfaces import (
    AlignmentAdapter,
    CaptureProvider,
    DepositLookupProvider,
    OCRProvider,
    StatusCallback,
)
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.services.ocr_service import ocr_with_ollama
from scanning_tool.state.scan_state import ScanState
from scanning_tool.deposits import lookup_deposit
from scanning_tool.gui.overlays import (
    update_capture_overlay_region,
    sync_capture_sliders,
)


class ScreenCaptureProvider(CaptureProvider):
    """Capture a PIL image from a screen region."""

    def capture(self, region: CaptureRegion) -> Image.Image:
        with mss.mss() as sct:
            img = sct.grab(region.to_monitor())
            return Image.frombytes("RGB", img.size, img.rgb)


class OllamaOCRProvider(OCRProvider):
    """OCR adapter that delegates to the Ollama service."""

    def extract_text(self, pil_img: Image.Image) -> str:
        return ocr_with_ollama(pil_img)


class DepositLookupAdapter(DepositLookupProvider):
    """Adapter for deposit lookup from OCR code extraction."""

    def lookup(self, code: Optional[str]) -> Optional[DepositInfo]:
        return lookup_deposit(code)


class CaptureService:
    """Service for capturing screen regions and processing OCR results."""

    def __init__(self, config: ConfigData, scan_state: ScanState) -> None:
        self._config = config
        self._scan_state = scan_state
        self._capture_use_case = CaptureUseCase(
            config=config,
            scan_state=scan_state,
            capture_provider=ScreenCaptureProvider(),
            ocr_provider=OllamaOCRProvider(),
            deposit_lookup=DepositLookupAdapter(),
            alignment_adapter=cast(AlignmentAdapter, alignment_service),
            sync_capture_sliders=sync_capture_sliders,
            update_capture_overlay_region=update_capture_overlay_region,
        )

    def capture_once(self, status_callback: Optional[StatusCallback] = None) -> None:
        """Capture one scan from the capture region and update overlay."""
        self._capture_use_case.capture_once(status_callback=status_callback)

    def toggle_continuous(self) -> None:
        """Toggle continuous scanning mode."""
        self._scan_state.continuous_mode = not self._scan_state.continuous_mode
        logger.info(f"Continuous mode: {self._scan_state.continuous_mode}")

        if self._scan_state.continuous_mode:
            Thread(target=self._continuous_scan_loop, daemon=True).start()

    def _continuous_scan_loop(self) -> None:
        """Run scans repeatedly until continuous_mode is turned off."""
        while self._scan_state.continuous_mode:
            self.capture_once()
            interval = max(0.1, float(self._config.continuous_capture_interval))
            time.sleep(interval)
