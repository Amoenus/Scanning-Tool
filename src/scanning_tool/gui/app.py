"""Main application entry: assembles the Tk root and all GUI sections."""

import tkinter as tk
from tkinter import ttk

from scanning_tool.gui.alignment import AlignmentPoller
from scanning_tool.gui.lifecycle import register_close_handler
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
from scanning_tool.gui.theme import apply_glass_theme
from scanning_tool.gui.widgets import ScrollableFrame
from scanning_tool.gui.overlays import show_overlay


# Section build order — matches the original top-to-bottom layout.
SECTION_CLASSES = (
    CaptureRegionSection,
    HeadSwaySection,
    OllamaSection,
    ResultDisplaySection,
    ControlsSection,
)


def launch_gui(
    config,
    scan_state,
    service_state,
    overlay_state,
    control_state,
    capture_service,
    save_config,
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

    for section_cls in SECTION_CLASSES:
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
