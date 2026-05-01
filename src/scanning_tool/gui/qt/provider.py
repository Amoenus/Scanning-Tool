from __future__ import annotations

from typing import TYPE_CHECKING

from scanning_tool.gui.qt.app import launch_gui as launch_qt_gui

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


class QtGuiProvider:
    """PyQt6 GUI provider implementation."""

    provider_name = "qt"

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
        """Launch the PyQt6 GUI.

        Parameters
        ----------
        config : ConfigData
            Configuration data.
        scan_state : ScanState
            Current scan state.
        service_state : ServiceState
            Current service state.
        overlay_state : OverlayState
            Current overlay state.
        control_state : ControlState
            Current control state.
        capture_service : CaptureController
            Capture controller service.
        config_service : ConfigSaver
            Configuration saver service.

        """
        launch_qt_gui(
            config=config,
            scan_state=scan_state,
            service_state=service_state,
            overlay_state=overlay_state,
            control_state=control_state,
            capture_service=capture_service,
            config_service=config_service,
        )
