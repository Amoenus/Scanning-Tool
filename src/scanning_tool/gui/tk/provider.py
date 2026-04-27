from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState

    from ..control_state import ControlState
    from ..overlay_state import OverlayState
class TkGuiProvider:
    """Tkinter GUI provider implementation."""

    provider_name = "tk"

    def launch_gui(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        overlay_state: OverlayState,
        control_state: ControlState,
        capture_service: CaptureController,
        config_service: ConfigSaver,
    ) -> None:
        from scanning_tool.gui.tk.app import launch_gui as launch_tk_gui

        launch_tk_gui(
            config=config,
            scan_state=scan_state,
            service_state=service_state,
            overlay_state=overlay_state,
            control_state=control_state,
            capture_service=capture_service,
            config_service=config_service,
        )
