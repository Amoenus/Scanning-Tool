from types import SimpleNamespace

from pytest import MonkeyPatch

from scanning_tool.config.service import ConfigData
from scanning_tool.gui import handlers as gui_handlers
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.event_handlers import install_ui_action_handlers
from scanning_tool.state.actions import ConfigAction


class DummyConfigService:
    def __init__(self) -> None:
        self.saved = False

    def save(self) -> None:
        self.saved = True


def test_save_config_action_triggers_config_save_handler() -> None:
    config = ConfigData()
    scan_state = SimpleNamespace()
    service_state = SimpleNamespace()
    overlay_state = SimpleNamespace()
    control_state = SimpleNamespace()
    capture_service = SimpleNamespace()
    config_service = DummyConfigService()

    install_ui_action_handlers(
        config=config,  # type: ignore
        scan_state=scan_state,  # type: ignore
        service_state=service_state,  # type: ignore
        overlay_state=overlay_state,  # type: ignore
        control_state=control_state,  # type: ignore
        capture_service=capture_service,  # type: ignore
        config_service=config_service,  # type: ignore
    )

    publish_ui_action(ConfigAction.SAVE_CONFIG)

    assert config_service.saved is True


def test_update_overlay_region_action_invokes_handler(monkeypatch: MonkeyPatch) -> None:
    config = ConfigData()
    scan_state = SimpleNamespace()
    service_state = SimpleNamespace()
    overlay_state = SimpleNamespace()
    control_state = SimpleNamespace()
    capture_service = SimpleNamespace()
    config_service = DummyConfigService()
    called = []

    def fake_update_overlay_region(payload, context):
        called.append(context.overlay_state)

    monkeypatch.setitem(
        gui_handlers.ACTION_HANDLERS,
        ConfigAction.UPDATE_OVERLAY_REGION,
        fake_update_overlay_region,
    )

    install_ui_action_handlers(
        config=config,  # type: ignore
        scan_state=scan_state,  # type: ignore
        service_state=service_state,  # type: ignore
        overlay_state=overlay_state,  # type: ignore
        control_state=control_state,  # type: ignore
        capture_service=capture_service,  # type: ignore
        config_service=config_service,  # type: ignore
    )

    publish_ui_action(ConfigAction.UPDATE_OVERLAY_REGION)

    assert called == [overlay_state]


def test_choose_label_color_action_invokes_handler(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("tkinter.colorchooser.askcolor", lambda **kwargs: (None, "#ffffff"))

    config = ConfigData()
    scan_state = SimpleNamespace()
    service_state = SimpleNamespace()
    overlay_state = SimpleNamespace()
    control_state = SimpleNamespace()
    capture_service = SimpleNamespace()
    config_service = DummyConfigService()
    called = []

    def fake_choose_label_color(payload, context):
        called.append(context.config.overlay_config)

    monkeypatch.setitem(
        gui_handlers.ACTION_HANDLERS,
        ConfigAction.CHOOSE_LABEL_COLOR,
        fake_choose_label_color,
    )

    install_ui_action_handlers(
        config=config,  # type: ignore
        scan_state=scan_state,  # type: ignore
        service_state=service_state,  # type: ignore
        overlay_state=overlay_state,  # type: ignore
        control_state=control_state,  # type: ignore
        capture_service=capture_service,  # type: ignore
        config_service=config_service,  # type: ignore
    )

    publish_ui_action(ConfigAction.CHOOSE_LABEL_COLOR)

    assert called == [config.overlay_config]
