"""Main application entry: launches the Tkinter GUI and builds its sections."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from typing import TYPE_CHECKING

from scanning_tool.gui.event_handlers import install_ui_action_handlers
from scanning_tool.gui.tk.alignment import AlignmentPoller
from scanning_tool.gui.tk.lifecycle import register_close_handler
from scanning_tool.gui.tk.overlays import (
    configure_capture_slider_sync,
    install_edit_mode_overlay,
    register_overlay_signal_handlers,
    show_overlay,
    update_overlay_label,
)
from scanning_tool.gui.tk.overlays.base import safe_tk
from scanning_tool.gui.tk.sections import (
    ControlsSection,
    MobileOverlaySection,
    Section,
    SectionContext,
    SettingsSection,
    StatusOverviewSection,
)
from scanning_tool.gui.tk.status import StatusBar
from scanning_tool.gui.tk.theme import GlassPalette, apply_glass_theme
from scanning_tool.gui.tk.widgets import ScrollableFrame
from scanning_tool.state.signals import (
    alignment_applied_signal,
    sync_capture_sliders_signal,
    update_capture_overlay_region_signal,
)

if TYPE_CHECKING:
    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.domain.capture import ScanResult
    from scanning_tool.gui.tk.control_state import ControlState
    from scanning_tool.gui.tk.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState
SECTION_CLASSES: Sequence[type[Section]] = (
    ControlsSection,
    MobileOverlaySection,
    StatusOverviewSection,
    SettingsSection,
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

    install_ui_action_handlers(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        overlay_state=overlay_state,
        control_state=control_state,
        capture_service=capture_service,
        config_service=config_service,
    )
    register_overlay_signal_handlers()
    edit_mode_overlay_manager = install_edit_mode_overlay(
        ctx.overlay_state,
        ctx.control_state,
        ctx.config,
    )
    setattr(root, "edit_mode_overlay_manager", edit_mode_overlay_manager)
    configure_capture_slider_sync(
        ctx.control_state,
        lambda: ctx.config.capture_region,
    )

    def _on_alignment_applied(sender: object, event: object | None = None) -> None:
        sync_capture_sliders_signal.send(sender)
        update_capture_overlay_region_signal.send(sender)

    alignment_applied_signal.connect(_on_alignment_applied, weak=False)

    main = _build_main_panel(root, colors)
    _build_sections(main, ctx)

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
