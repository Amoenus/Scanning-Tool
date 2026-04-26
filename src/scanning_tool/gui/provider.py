from __future__ import annotations

import importlib
from typing import Protocol, TYPE_CHECKING

from loguru import logger
from scanning_tool.config.service import ConfigData, ConfigSaver
from scanning_tool.interfaces import CaptureController

if TYPE_CHECKING:
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


DEFAULT_GUI_BACKEND = "tk"
GUI_PROVIDER_REGISTRY: dict[str, tuple[str, str]] = {
    "tk": ("scanning_tool.gui.tk.provider", "TkGuiProvider"),
}


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
    ) -> None: ...


def get_default_gui_provider(config: ConfigData | None = None) -> GuiProvider:
    """Return the default GUI provider for the current runtime implementation."""
    selected_backend = _select_gui_backend(config)
    provider_cls = _resolve_gui_provider_class(selected_backend)
    return provider_cls()


def _select_gui_backend(config: ConfigData | None = None) -> str:
    if config is not None and config.gui_backend:
        return config.gui_backend.strip().lower()

    return DEFAULT_GUI_BACKEND


def _resolve_gui_provider_class(backend: str) -> type[GuiProvider]:
    if backend not in GUI_PROVIDER_REGISTRY:
        logger.warning(
            "Unsupported GUI backend requested, falling back to Tkinter.",
            backend=backend,
        )
        backend = DEFAULT_GUI_BACKEND

    module_name, class_name = GUI_PROVIDER_REGISTRY[backend]
    try:
        module = importlib.import_module(module_name)
        provider_cls = getattr(module, class_name)
        return provider_cls
    except (ImportError, AttributeError) as exc:
        if backend != DEFAULT_GUI_BACKEND:
            logger.warning(
                "Failed to load requested GUI backend, falling back to Tkinter.",
                backend=backend,
                error=exc,
            )
        module_name, class_name = GUI_PROVIDER_REGISTRY[DEFAULT_GUI_BACKEND]
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
