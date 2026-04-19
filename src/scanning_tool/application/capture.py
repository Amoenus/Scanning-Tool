from __future__ import annotations

import re
from typing import Optional

from loguru import logger
from PIL.Image import Image

from scanning_tool.config.service import ConfigData
from scanning_tool.deposits import extract_code_from_text
from scanning_tool.domain.alignment import AlignmentRequest, CaptureRegion
from scanning_tool.domain.capture import CodeExtraction, ScanResult
from scanning_tool.interfaces.capture import (
    AlignmentAdapter,
    CaptureProvider,
    DepositLookupProvider,
    OCRProvider,
    StatusCallback,
)
from scanning_tool.state.scan_state import ScanState


class ScanPipeline:
    """Builds a scan result by running OCR and resolving deposit metadata."""

    def __init__(
        self,
        ocr_provider: OCRProvider,
        deposit_lookup: DepositLookupProvider,
        capture_region: CaptureRegion,
    ) -> None:
        self._ocr_provider = ocr_provider
        self._deposit_lookup = deposit_lookup
        self._capture_region = capture_region

    def scan(self, pil_img: Image) -> ScanResult:
        raw_text = self._ocr_provider.extract_text(pil_img)
        extraction: CodeExtraction = extract_code_from_text(raw_text)
        deposit_info = self._deposit_lookup.lookup(extraction.code)

        return ScanResult(
            label=extraction.code if extraction.code else "UNKNOWN",
            region=self._capture_region,
            info=deposit_info,
            code_raw=extraction.raw,
            raw_text=raw_text,
        )


class CaptureUseCase:
    """Orchestrates capture, OCR, and deposit lookup without UI logic."""

    def __init__(
        self,
        config: ConfigData,
        scan_state: ScanState,
        capture_provider: CaptureProvider,
        ocr_provider: OCRProvider,
        deposit_lookup: DepositLookupProvider,
        alignment_adapter: AlignmentAdapter,
    ) -> None:
        self._config = config
        self._scan_state = scan_state
        self._capture_provider = capture_provider
        self._ocr_provider = ocr_provider
        self._deposit_lookup = deposit_lookup
        self._alignment_adapter = alignment_adapter
        self._scan_pipeline = ScanPipeline(
            ocr_provider=ocr_provider,
            deposit_lookup=deposit_lookup,
            capture_region=config.capture_region,
        )
        self._status_callback: Optional[StatusCallback] = None

    def capture_once(self, status_callback: Optional[StatusCallback] = None) -> None:
        """Capture a single scan and populate the shared scan state."""
        self._status_callback = status_callback
        self._do_capture()

    def _highlight_numbers(self, text: str) -> str:
        """Wrap numbers in <yellow> tags for log output."""
        return re.sub(r"(\d+)", r"<yellow>\1</yellow>", text)

    def _set_status(self, message: str) -> None:
        if self._status_callback:
            self._status_callback(message)

    def _align_before_capture(self) -> None:
        self._set_status("Aligning region...")
        self._alignment_adapter.align(
            self._scan_state.anchor_tracker,
            self._scan_state.last_alignment_info,
            AlignmentRequest.from_config(self._config),
        )

    def _capture_screen_region(self) -> Image:
        return self._capture_provider.capture(self._config.capture_region)

    def _run_scan_pipeline(self, pil_img: Image) -> ScanResult:
        return self._scan_pipeline.scan(pil_img)

    def _log_scan_result(self, result: ScanResult) -> None:
        logger.info(
            "Scan result: ScanResult(label={}, region={}, code_raw={}, raw_text={})",
            result.label,
            result.region,
            result.code_raw,
            result.raw_text,
        )
        logger.debug("Deposit info: {}", result.info)
        self._set_status(self._highlight_numbers(
            f"Scan result: ScanResult(label={result.label}, region={result.region}, code_raw={result.code_raw}, raw_text={result.raw_text})"
        ))

    def _do_capture(self) -> None:
        self._align_before_capture()
        pil_img = self._capture_screen_region()
        self._set_status("Loading OCR model (may take a moment)...")
        logger.info("Starting OCR capture pipeline.")
        try:
            self._scan_state.last_result = self._run_scan_pipeline(pil_img)
            self._log_scan_result(self._scan_state.last_result)
            self._set_status("Scan complete.")
        except Exception as exc:  # pragma: no cover
            logger.error("OCR/model error: {}", exc)
            self._set_status(f"OCR/model error: {exc}")
