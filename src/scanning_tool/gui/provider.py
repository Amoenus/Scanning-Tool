from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from scanning_tool.config.service import ConfigData, ConfigSaver
from scanning_tool.interfaces import CaptureController

if TYPE_CHECKING:
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


class GuiProvider(Protocol):
    """Interface for a pluggable GUI provider."""

    provider_name: str

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
        ...


def get_default_gui_provider() -> GuiProvider:
    """Return the default GUI provider for the current runtime implementation."""
    from scanning_tool.gui.tk.provider import TkGuiProvider

    return TkGuiProvider()
