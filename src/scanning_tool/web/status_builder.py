from __future__ import annotations

from typing import Optional

from scanning_tool.config.service import ConfigData
from scanning_tool.domain.capture import DepositInfo
from scanning_tool.interfaces.web import StatusResponseBuilder
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.web.schemas import DepositTable, StatusResponse


class DefaultStatusResponseBuilder(StatusResponseBuilder):
    """Builds the overlay status response from runtime state."""

    def build_status_response(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        selected_region: str,
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
        )

    def _lookup_deposit_table(
        self,
        info: Optional[DepositInfo],
        selected_region: str,
        service_state: ServiceState,
    ) -> Optional[DepositTable]:
        if not info:
            return None

        deposit_key = (info.key or info.name or "").upper()
        region_tables = service_state.rocks.deposit_tables.get(selected_region, {})
        table = region_tables.get(deposit_key)
        category = str(info.category or "").lower()
        if not table or category not in {"rock deposits", "gems"}:
            return None
        return table
