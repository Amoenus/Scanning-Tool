from __future__ import annotations

from re import Pattern

from loguru import logger
from PIL.Image import Image

from scanning_tool.application.scan_result_reporter import ScanResultReporter
from scanning_tool.deposits import extract_code_from_text
from scanning_tool.domain.alignment import AlignmentRequest, CaptureRegion
from scanning_tool.domain.capture import CodeExtraction, ScanResult
from scanning_tool.state.service_state import ServiceState
from scanning_tool.state.signals import status_updated


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.interfaces.capture import AlignmentAdapter, CaptureProvider, DepositLookupProvider, OCRProvider, StatusCallback
    from scanning_tool.config.service import ConfigData
class ScanPipeline:
    """Builds a scan result by running OCR and resolving deposit metadata."""

    def __init__(
        self,
        ocr_provider: OCRProvider,
        deposit_lookup: DepositLookupProvider,
        capture_region: CaptureRegion,
        code_re: Pattern[str],
    ) -> None:
        self._ocr_provider = ocr_provider
        self._deposit_lookup = deposit_lookup
        self._capture_region = capture_region
        self._code_re = code_re

    def scan(self, pil_img: Image) -> ScanResult:
        raw_text = self._ocr_provider.extract_text(pil_img)
        extraction: CodeExtraction = extract_code_from_text(raw_text, self._code_re)
        deposit_info = self._deposit_lookup.lookup(extraction.code)

        return ScanResult(
            label=extraction.code or "UNKNOWN",
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
        code_re: Pattern[str] | None = None,
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
            code_re=code_re or ServiceState().code_re,
        )

    def capture_once(self, status_callback: StatusCallback | None = None) -> None:
        """Capture a single scan and populate the shared scan state."""
        if status_callback is None:
            self._do_capture()
            return

        def _receiver(sender: object, message: str) -> None:
            status_callback(message)

        status_updated.connect(_receiver, weak=False)
        try:
            self._do_capture()
        finally:
            status_updated.disconnect(_receiver)

    def _set_status(self, message: str) -> None:
        status_updated.send(self, message=message)

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

    def _report_scan_result(self, result: ScanResult) -> None:
        ScanResultReporter.log(result)
        self._set_status(ScanResultReporter.format_status_message(result))
        logger.debug("Deposit info: {}", result.info)

    def _capture_and_report(self, pil_img: Image) -> ScanResult:
        result = self._run_scan_pipeline(pil_img)
        self._report_scan_result(result)
        return result

    def _do_capture(self) -> None:
        self._align_before_capture()
        pil_img = self._capture_screen_region()
        self._set_status("Loading OCR model (may take a moment)...")
        logger.info("Starting OCR capture pipeline.")
        try:
            self._scan_state.last_result = self._capture_and_report(pil_img)
            self._set_status("Scan complete.")
        except Exception as exc:  # pragma: no cover
            logger.error("OCR/model error: {}", exc)
            self._set_status(f"OCR/model error: {exc}")
