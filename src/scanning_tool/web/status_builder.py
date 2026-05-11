from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from scanning_tool.interfaces.web import StatusResponseBuilder
from scanning_tool.web.schemas import DepositTable, StatusResponse

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData
    from scanning_tool.domain.capture import DepositInfo, ScanResult
    from scanning_tool.domain.common import SpaceSystem
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
SUPPORTED_DEPOSIT_CATEGORIES = {"rock deposits", "gems"}


class DepositTableResolver:
    """Resolve deposit tables from service state for a selected region."""

    def resolve(
        self,
        info: DepositInfo | None,
        selected_region: SpaceSystem,
        service_state: ServiceState,
    ) -> DepositTable | None:
        if info is None:
            return None

        deposit_key = self._deposit_key(info)
        region_tables = service_state.rocks.deposit_tables.get(selected_region, {})
        table = region_tables.get(deposit_key)
        category = self._deposit_category(info)

        return table if self._is_supported_deposit_category(table, category) else None

    @staticmethod
    def _deposit_key(info: DepositInfo) -> str:
        return (info.key or info.name or "").upper()

    @staticmethod
    def _deposit_category(info: DepositInfo) -> str:
        return str(info.category or "").lower()

    @staticmethod
    def _is_supported_deposit_category(
        table: DepositTable | None,
        category: str,
    ) -> bool:
        return bool(table) and category in SUPPORTED_DEPOSIT_CATEGORIES


class DefaultStatusResponseBuilder(StatusResponseBuilder):
    """Builds the overlay status response from runtime state."""

    def __init__(
        self,
        deposit_table_resolver: DepositTableResolver | None = None,
    ) -> None:
        self._deposit_table_resolver = deposit_table_resolver or DepositTableResolver()

    def build_status_response(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        selected_region: SpaceSystem,
    ) -> StatusResponse:
        result = scan_state.last_result
        info = result.info if result else None
        table = self._lookup_deposit_table(info, selected_region, service_state)
        return StatusResponse(
            region=config.capture_region,
            label_color=config.overlay_config.label_color,
            last=result,
            alignment=scan_state.last_alignment_info,
            selected_region=selected_region,
            info=info,
            code=result.label if result else None,
            code_raw=result.code_raw if result else None,
            raw_text=result.raw_text if result else None,
            table=table,
            status=self._derive_status(result),
            updated_at=datetime.utcnow().replace(microsecond=0),
        )

    @staticmethod
    def _derive_status(result: ScanResult | None) -> str:
        if result is None:
            return "no_scan"
        if result.info is None:
            return "invalid_scan"
        return "ok"

    def _lookup_deposit_table(
        self,
        info: DepositInfo | None,
        selected_region: SpaceSystem,
        service_state: ServiceState,
    ) -> DepositTable | None:
        return self._deposit_table_resolver.resolve(
            info,
            selected_region,
            service_state,
        )
