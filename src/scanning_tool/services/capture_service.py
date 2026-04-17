"""Service for handling screen capture and OCR processing."""

import re
import time
from threading import Thread
from typing import Callable, Optional

import mss
from loguru import logger
from PIL import Image

from scanning_tool.config.service import ConfigData
from scanning_tool.state.scan_state import ScanState
from scanning_tool.services.ocr_service import ocr_with_ollama
from scanning_tool.deposits import extract_code_from_text, lookup_deposit
from scanning_tool.services.alignment_service import alignment_service
from scanning_tool.domain.alignment import AlignmentRequest, CaptureRegion
from scanning_tool.domain.capture import ScanResult
from scanning_tool.gui.overlays import (
    update_capture_overlay_region,
    update_overlay_label,
    sync_capture_sliders,
)


CaptureStatusCallback = Callable[[str], None]


class ScreenCaptureProvider:
    """Capture a PIL image from a screen region."""

    def capture(self, region: CaptureRegion) -> Image.Image:
        with mss.mss() as sct:
            img = sct.grab(region.to_monitor())
            return Image.frombytes("RGB", img.size, img.rgb)


class ScanResultFactory:
    """Create a ScanResult from OCR output and deposit lookup."""

    def build_from_image(self, pil_img: Image.Image, region: CaptureRegion) -> ScanResult:
        raw_text = ocr_with_ollama(pil_img)
        extraction = extract_code_from_text(raw_text)
        deposit_info = lookup_deposit(extraction.code)

        result = ScanResult(
            label=extraction.code if extraction.code else "UNKNOWN",
            region=region,
            info=deposit_info,
            code_raw=extraction.raw,
            raw_text=raw_text,
        )

        update_overlay_label(
            deposit_info, code=extraction.code, raw_text=extraction.raw or raw_text
        )
        return result


class CaptureService:
    """Service for capturing screen regions and processing OCR results."""

    def __init__(self, config: ConfigData, scan_state: ScanState) -> None:
        self._status_callback: Optional[CaptureStatusCallback] = None
        self._screen_capture_provider = ScreenCaptureProvider()
        self._scan_result_factory = ScanResultFactory()
        self._config = config
        self._scan_state = scan_state

    def capture_once(self, status_callback: Optional[CaptureStatusCallback] = None) -> None:
        """Capture one scan from the capture region and update overlay."""
        self._status_callback = status_callback
        self._do_capture()

    def _highlight_numbers(self, text: str) -> str:
        """Wrap numbers in <yellow> tags for loguru."""
        return re.sub(r"(\d+)", r"<yellow>\1</yellow>", text)

    def _set_status(self, message: str) -> None:
        if self._status_callback:
            self._status_callback(message)

    def _align_before_capture(self) -> None:
        self._set_status("Aligning region...")
        auto_aligned = alignment_service.align(
            self._scan_state.anchor_tracker,
            self._scan_state.last_alignment_info,
            AlignmentRequest.from_config(self._config),
            sync_capture_sliders,
            update_capture_overlay_region,
        )
        if self._config.auto_alignment.enabled:
            logger.debug(
                "Auto alignment %s before capture.",
                "succeeded" if auto_aligned else "did not match",
            )

    def _capture_screen_region(self) -> Image.Image:
        return self._screen_capture_provider.capture(self._config.capture_region)

    def _run_ocr_pipeline(self, pil_img: Image.Image) -> ScanResult:
        return self._scan_result_factory.build_from_image(
            pil_img, self._config.capture_region
        )

    def _log_scan_result(self, result: ScanResult) -> None:
        logger.info(
            f"Scan result: ScanResult("
            f"label={result.label}, "
            f"region={result.region}, "
            f"code_raw={result.code_raw}, "
            f"raw_text={result.raw_text}"
            ")"
        )

    def _do_capture(self):
        self._align_before_capture()
        pil_img = self._capture_screen_region()
        self._set_status("Loading OCR model (may take a moment)...")
        logger.debug("Loading OCR model for scan...")
        try:
            self._scan_state.last_result = self._run_ocr_pipeline(pil_img)
            self._log_scan_result(self._scan_state.last_result)
            self._set_status("Scan complete.")
        except Exception as e:
            logger.error(f"OCR/model error: {e}")
            self._set_status(f"OCR/model error: {e}")

    def toggle_continuous(self) -> None:
        """Toggle continuous scanning mode."""
        self._scan_state.continuous_mode = not self._scan_state.continuous_mode
        logger.info(f"Continuous mode: {self._scan_state.continuous_mode}")

        if self._scan_state.continuous_mode:
            Thread(target=self._continuous_scan_loop, daemon=True).start()

    def _continuous_scan_loop(self) -> None:
        """Run scans repeatedly until continuous_mode is turned off."""
        while True:
            if not self._scan_state.continuous_mode:
                break
            self.capture_once()
            interval = max(0.1, float(self._config.continuous_capture_interval))
            time.sleep(interval)
