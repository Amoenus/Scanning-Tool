"""Main application entry: launches the Tkinter GUI and builds its sections."""

from typing import Sequence, Type

import tkinter as tk
from tkinter import ttk

from scanning_tool.config.service import ConfigData
from scanning_tool.gui.alignment import AlignmentPoller
from scanning_tool.gui.lifecycle import register_close_handler
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.gui.sections import (
    CaptureRegionSection,
    ControlsSection,
    HeadSwaySection,
    OllamaSection,
    ResultDisplaySection,
    Section,
    SectionContext,
)
from scanning_tool.gui.status import StatusBar
from scanning_tool.gui.theme import GlassPalette, apply_glass_theme
from scanning_tool.gui.widgets import ScrollableFrame
from scanning_tool.gui.overlays import show_overlay
from scanning_tool.interfaces import CaptureController
from scanning_tool.state.scan_state import ScanState
from scanning_tool.state.service_state import ServiceState
from scanning_tool.gui.control_state import ControlState


SECTION_CLASSES: Sequence[Type[Section]] = (
    CaptureRegionSection,
    HeadSwaySection,
    OllamaSection,
    ResultDisplaySection,
    ControlsSection,
)


def launch_gui(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    save_config,
) -> None:
    """Build and run the main Tkinter control panel."""
    root = _create_root()
    register_close_handler(root, overlay_state, save_config)

    colors = apply_glass_theme(root)
    status = StatusBar(root)
    status.install_as_scanning_callback(service_state)

    ctx = _build_section_context(
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

    main = _build_main_panel(root, colors, ctx)
    _build_sections(main, ctx)
    _append_status_labels(main, status)

    root.update_idletasks()
    show_overlay(root.winfo_screenwidth(), root.winfo_screenheight())
    AlignmentPoller(root, status, config, scan_state).start()
    root.mainloop()


def _create_root() -> tk.Tk:
    window = tk.Tk()
    window.title("Star Citizen Scanner Control")
    return window


def _build_section_context(
    *,
    root: tk.Tk,
    colors: GlassPalette,
    status: StatusBar,
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    save_config,
) -> SectionContext:
    return SectionContext(
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


def _build_main_panel(root: tk.Tk, colors: GlassPalette, ctx: SectionContext) -> tk.Widget:
    scroll = ScrollableFrame(root, colors)
    return scroll.inner


def _build_sections(main: tk.Widget, ctx: SectionContext) -> None:
    for section_cls in SECTION_CLASSES:
        section_cls().build(main, ctx)


def _append_status_labels(main: tk.Widget, status: StatusBar) -> None:
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
