from types import SimpleNamespace

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.event_handlers import install_ui_action_handlers


class DummyConfigService:
    def __init__(self) -> None:
        self.saved = False

    def save(self) -> None:
        self.saved = True


def test_save_config_action_triggers_config_save_handler() -> None:
    config = SimpleNamespace()
    scan_state = SimpleNamespace()
    service_state = SimpleNamespace()
    overlay_state = SimpleNamespace()
    control_state = SimpleNamespace()
    capture_service = SimpleNamespace()
    config_service = DummyConfigService()

    install_ui_action_handlers(
        config=config,
        scan_state=scan_state,
        service_state=service_state,
        overlay_state=overlay_state,
        control_state=control_state,
        capture_service=capture_service,
        config_service=config_service,
    )

    publish_ui_action(UiActionType.SAVE_CONFIG)

    assert config_service.saved is True
