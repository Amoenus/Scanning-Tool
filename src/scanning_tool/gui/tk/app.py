"""Main application entry: launches the Tkinter GUI and builds its sections."""
from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from tkinter import ttk
from typing import TYPE_CHECKING

from .alignment import AlignmentPoller
from .lifecycle import register_close_handler
from .overlays import (
    configure_capture_slider_sync,
    show_overlay,
    sync_capture_sliders_callback,
    update_capture_overlay_region,
    update_overlay_label,
)
from .overlays.base import safe_tk
from .sections import (
    CaptureRegionSection,
    ControlsSection,
    HeadSwaySection,
    MobileOverlaySection,
    OllamaSection,
    ResultDisplaySection,
    Section,
    SectionContext,
    StatusOverviewSection,
)
from .status import StatusBar
from .theme import GlassPalette, apply_glass_theme
from .widgets import ScrollableFrame

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.domain.capture import ScanResult
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState

    from .control_state import ControlState
    from .overlay_state import OverlayState
SECTION_CLASSES: Sequence[type[Section]] = (
    CaptureRegionSection,
    HeadSwaySection,
    OllamaSection,
    StatusOverviewSection,
    ResultDisplaySection,
    ControlsSection,
    MobileOverlaySection,
)


def launch_gui(
    config: ConfigData,
    scan_state: ScanState,
    service_state: ServiceState,
    overlay_state: OverlayState,
    control_state: ControlState,
    capture_service: CaptureController,
    config_service: ConfigSaver,
) -> None:
    """Build and run the main Tkinter control panel."""
    root = _create_root()
    register_close_handler(root, overlay_state, config_service)

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
        config_service=config_service,
    )
    configure_capture_slider_sync(
        ctx.control_state,
        lambda: ctx.config.capture_region,
    )

    from scanning_tool.state.signals import alignment_applied_signal

    def _on_alignment_applied(sender: object, event: object | None = None) -> None:
        sync_capture_sliders_callback()
        update_capture_overlay_region()

    alignment_applied_signal.connect(_on_alignment_applied, weak=False)

    main = _build_main_panel(root, colors)
    _build_sections(main, ctx)
    _append_status_labels(main, status)

    root.update_idletasks()

    def _refresh_overlay_label(scan_result: ScanResult | None) -> None:
        update_overlay_label(
            scan_result.info if scan_result else None,
            ctx.overlay_state,
            ctx.config.overlay_config,
            code=scan_result.label if scan_result else None,
            raw_text=scan_result.code_raw if scan_result else None,
        )

    def _on_scan_result_change(scan_result: ScanResult | None) -> None:
        safe_tk(
            lambda: root.after(0, lambda: _refresh_overlay_label(scan_result)),
        )

    scan_state.add_scan_result_listener(_on_scan_result_change)
    _refresh_overlay_label(scan_state.last_result)

    show_overlay(
        ctx.overlay_state,
        ctx.config,
        root.winfo_screenwidth(),
        root.winfo_screenheight(),
    )
    AlignmentPoller(root, status, config, scan_state).start()
    root.mainloop()


def _create_root() -> tk.Tk:
    window = tk.Tk()
    window.title("Star Citizen Scanner Control")
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
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
    config_service: ConfigSaver,
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
        config_service=config_service,
    )


def _build_main_panel(root: tk.Tk, colors: GlassPalette) -> tk.Widget:
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
