from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QMainWindow, QScrollArea, QVBoxLayout, QWidget

from scanning_tool.gui.event_handlers import install_ui_action_handlers
from scanning_tool.gui.overlays import configure_capture_slider_sync, show_overlay
from scanning_tool.gui.qt.sections import (
    ControlsSection,
    MobileOverlaySection,
    SectionContext,
    SettingsSection,
    StatusOverviewSection,
)
from scanning_tool.gui.qt.status import StatusBar

if TYPE_CHECKING:
    from PyQt6.QtCore import QRect
    from PyQt6.QtGui import QScreen

    from scanning_tool.config.service import ConfigData, ConfigSaver
    from scanning_tool.gui.control_state import ControlState
    from scanning_tool.gui.overlay_state import OverlayState
    from scanning_tool.interfaces import CaptureController
    from scanning_tool.state.scan_state import ScanState
    from scanning_tool.state.service_state import ServiceState


SECTION_CLASSES = (
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
    """Build and run the main PyQt6 control panel."""
    app = QApplication.instance() or QApplication([])

    window = QMainWindow()
    window.setWindowTitle("Star Citizen Scanner Control")
    window.resize(820, 600)

    root_widget = QWidget()
    layout = QVBoxLayout(root_widget)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    status = StatusBar()
    status.install_as_scanning_callback(service_state)

    ctx = SectionContext(
        root=root_widget,
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

    configure_capture_slider_sync(
        ctx.control_state,
        lambda: ctx.config.capture_region,
    )

    for section_cls in SECTION_CLASSES:
        section = section_cls()
        widget = section.build(root_widget, ctx)
        layout.addWidget(widget)

    main_container = QWidget()
    main_container.setLayout(layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(main_container)

    window.setCentralWidget(scroll)
    window.show()

    screen: QScreen | None = window.screen() or app.primaryScreen()
    if screen is not None:
        geometry: QRect = screen.geometry()
        show_overlay(
            ctx.overlay_state,
            config,
            screen_width=geometry.width(),
            screen_height=geometry.height(),
        )
    else:
        show_overlay(ctx.overlay_state, config)

    app.exec()
