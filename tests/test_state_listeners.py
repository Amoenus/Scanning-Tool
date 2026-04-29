from __future__ import annotations

from scanning_tool.config.service import ConfigData
from scanning_tool.domain.capture import ScanResult
from scanning_tool.gui.overlay_state import OverlayState
from scanning_tool.state.scan_state import ScanState


def test_scan_state_scan_result_listener_is_called() -> None:
    scan_state = ScanState()
    received: list[ScanResult | None] = []

    scan_state.add_scan_result_listener(lambda result: received.append(result))

    expected = ScanResult(
        label="TEST",
        region=ConfigData().capture_region,
    )
    scan_state.last_result = expected

    assert received == [expected]


def test_scan_state_alignment_info_listener_is_called() -> None:
    scan_state = ScanState()
    received: list[bool] = []

    scan_state.add_alignment_info_listener(lambda info: received.append(info.enabled))

    scan_state.last_alignment_info.enabled = True
    scan_state.notify_alignment_info_listeners()

    assert received == [True]


def test_overlay_state_capture_root_listener_is_called() -> None:
    overlay_state = OverlayState()
    received: list[object | None] = []

    overlay_state.add_capture_overlay_root_listener(lambda root: received.append(root))

    root_object = object()
    overlay_state.capture_overlay_root = root_object
    overlay_state.capture_overlay_root = None

    assert received == [root_object, None]


def test_overlay_state_anchor_visibility_listener_is_called() -> None:
    overlay_state = OverlayState()
    received: list[bool] = []

    overlay_state.add_anchor_overlay_visibility_listener(lambda visible: received.append(visible))

    overlay_state.anchor_overlay_visible = False
    overlay_state.anchor_overlay_visible = True

    assert received == [False, True]


def test_overlay_state_show_border_listener_is_called() -> None:
    overlay_state = OverlayState()
    received: list[bool] = []

    overlay_state.add_show_border_listener(lambda visible: received.append(visible))

    overlay_state.show_border = False
    overlay_state.show_border = True

    assert received == [False, True]


def test_overlay_state_emits_capture_overlay_root_changed_signal() -> None:
    from scanning_tool.state.signals import capture_overlay_root_changed

    overlay_state = OverlayState()
    received: list[object | None] = []

    def receiver(sender: object, capture_root: object | None = None) -> None:
        received.append(capture_root)

    capture_overlay_root_changed.connect(receiver, weak=False)

    root_object = object()
    overlay_state.capture_overlay_root = root_object
    overlay_state.capture_overlay_root = None

    capture_overlay_root_changed.disconnect(receiver)
    assert received == [root_object, None]


def test_overlay_state_emits_overlay_text_updated_signal() -> None:
    from scanning_tool.state.signals import overlay_text_updated

    overlay_state = OverlayState()
    received: list[str] = []

    def receiver(sender: object, overlay_text: str = "") -> None:
        received.append(overlay_text)

    overlay_text_updated.connect(receiver, weak=False)

    overlay_state.overlay_text = "hello"
    overlay_state.overlay_text = "world"

    overlay_text_updated.disconnect(receiver)
    assert received == ["hello", "world"]


def test_overlay_state_emits_show_border_changed_signal() -> None:
    from scanning_tool.state.signals import show_border_changed

    overlay_state = OverlayState()
    received: list[bool] = []

    def receiver(sender: object, show_border: bool = False) -> None:
        received.append(show_border)

    show_border_changed.connect(receiver, weak=False)

    overlay_state.show_border = False
    overlay_state.show_border = True

    show_border_changed.disconnect(receiver)
    assert received == [False, True]


def test_overlay_state_info_root_listener_is_called() -> None:
    overlay_state = OverlayState()
    received: list[object | None] = []

    overlay_state.add_info_overlay_root_listener(lambda root: received.append(root))

    root_object = object()
    overlay_state.info_overlay_root = root_object
    overlay_state.info_overlay_root = None

    assert received == [root_object, None]


def test_gui_overlays_imports_generic_api_without_tk() -> None:
    from importlib import import_module

    overlays = import_module("scanning_tool.gui.overlays")

    assert hasattr(overlays, "toggle_border")
    assert hasattr(overlays, "start_label_timeout")
    assert hasattr(overlays, "show_overlay")
