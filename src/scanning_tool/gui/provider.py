from __future__ import annotations

from typing import Protocol, Callable, TYPE_CHECKING

from scanning_tool.config.service import ConfigData
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
        save_config: Callable[[], None],
    ) -> None:
        ...


def get_default_gui_provider() -> GuiProvider:
    """Return the default GUI provider for the current runtime implementation."""
    from scanning_tool.gui.tk.provider import TkGuiProvider

    return TkGuiProvider()
