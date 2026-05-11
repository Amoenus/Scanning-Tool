from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData
    from scanning_tool.domain.common import SpaceSystem
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
    from scanning_tool.web.schemas import StatusResponse


class StatusResponseBuilder(Protocol):
    """Builds a web response payload from application state."""

    def build_status_response(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        selected_region: SpaceSystem,
    ) -> StatusResponse: ...
