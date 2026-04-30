from scanning_tool.config.service import ConfigData
from scanning_tool.services.edit_mode_service import EditModeService
from scanning_tool.state import manager
from scanning_tool.state.actions import ConfigAction, EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion
from scanning_tool.state.signals import UI_ACTION_SIGNALS, edit_mode_changed, region_committed


def test_edit_mode_service_drags_and_commits_capture_region() -> None:
    service = EditModeService()
    service.start()

    committed = []
    config_payloads = []

    def collect_committed(sender: object, active_region=None, **kwargs: object) -> None:
        committed.append(active_region)

    def capture_handler(sender: object, payload=None, **kwargs: object) -> None:
        config_payloads.append(payload)

    region_committed.connect(collect_committed, weak=False)
    UI_ACTION_SIGNALS[ConfigAction.UPDATE_CAPTURE_REGION].connect(capture_handler, weak=False)

    UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].send(None)
    UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].send(None, left=100, top=120, width=300, height=200)
    UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].send(None)

    assert committed[-1] == ActiveRegion.CAPTURE
    assert config_payloads[0] == {"left": 100, "top": 120, "width": 300, "height": 200}
    assert config_payloads[-1] == {"left": 100, "top": 120, "width": 300, "height": 200}

    service.stop()


def test_edit_mode_service_resets_region_state() -> None:
    service = EditModeService()
    service.start()

    state_changes = []

    def collect_state(sender: object, state=None, **kwargs: object) -> None:
        state_changes.append(state)

    edit_mode_changed.connect(collect_state, weak=False)

    UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].send(None)
    UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].send(None, left=80, top=90, width=200, height=150)
    UI_ACTION_SIGNALS[EditModeAction.RESET_REGION].send(None)

    assert state_changes[-1].is_edit_mode
    assert state_changes[-1].active_region == ActiveRegion.CAPTURE

    service.stop()


def test_edit_mode_service_nudge_region_uses_current_config_values() -> None:
    service = EditModeService()
    service.start()

    manager.config = ConfigData()
    manager.config.capture_region.left = 100
    manager.config.capture_region.top = 200
    manager.config.capture_region.width = 300
    manager.config.capture_region.height = 100

    config_payloads = []

    def capture_handler(sender: object, payload=None, **kwargs: object) -> None:
        config_payloads.append(payload)

    UI_ACTION_SIGNALS[ConfigAction.UPDATE_CAPTURE_REGION].connect(capture_handler, weak=False)

    UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].send(None)
    UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].send(None, delta_left=1, delta_top=-2)

    assert config_payloads[-1] == {
        "left": 101,
        "top": 198,
    }

    service.stop()
