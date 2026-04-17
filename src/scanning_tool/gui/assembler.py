"""Factory for building and assembling GUI components."""

from typing import Callable

import tkinter as tk
from tkinter import ttk

from scanning_tool.config.service import ConfigData
from scanning_tool.gui.alignment import AlignmentPoller
from scanning_tool.gui.control_state import ControlState
from scanning_tool.gui.lifecycle import register_close_handler
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.gui.sections import (
    CaptureRegionSection,
    ControlsSection,
    HeadSwaySection,
    OllamaSection,
    ResultDisplaySection,
    SectionContext,
)
from scanning_tool.gui.status import StatusBar
from scanning_tool.gui.theme import apply_glass_theme
from scanning_tool.gui.widgets import ScrollableFrame
from scanning_tool.gui.overlays import show_overlay
from scanning_tool.services.capture_service import CaptureService
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState


class GUIFactory:
    """Factory for building and assembling the main GUI application."""

    def __init__(self):
        self._section_classes = (
            CaptureRegionSection,
            HeadSwaySection,
            OllamaSection,
            ResultDisplaySection,
            ControlsSection,
        )

    def create_gui(
        self,
        config: ConfigData,
        scan_state: ScanState,
        service_state: ServiceState,
        overlay_state: OverlayState,
        control_state: ControlState,
        capture_service: CaptureService,
        save_config: Callable[[], None],
    ) -> None:
        """Build and run the main Tkinter control panel."""
        root = tk.Tk()
        root.title("Star Citizen Scanner Control")
        register_close_handler(root, overlay_state, save_config)

        colors = apply_glass_theme(root)
        status = StatusBar(root)
        status.install_as_scanning_callback(service_state)
        ctx = SectionContext(
            root=root,
            colors=colors,
            status=status,
            config=config,
            scan_state=scan_state,
            service_state=service_state,
            overlay_state=overlay_state,
            control_state=control_state,
            capture_service=capture_service,
            save_config=save_config,
        )

        scroll = ScrollableFrame(root, colors)
        main = scroll.inner

        for section_cls in self._section_classes:
            section_cls().build(main, ctx)

        ttk.Label(
            main,
            textvariable=status.status_var,
            anchor="w",
            justify="left",
            style="Glass.Status.TLabel",
        ).pack(fill="x", padx=5, pady=(8, 0))
        ttk.Label(
            main,
            textvariable=status.anchor_status_var,
            anchor="w",
            justify="left",
            style="Glass.Subtle.TLabel",
        ).pack(fill="x", padx=5, pady=(2, 5))

        root.update_idletasks()
        show_overlay(root.winfo_screenwidth(), root.winfo_screenheight())
        AlignmentPoller(root, status, config, scan_state).start()
        root.mainloop()
