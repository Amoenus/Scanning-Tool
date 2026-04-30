from scanning_tool.services.edit_mode_service import EditModeService
from scanning_tool.state.actions import ConfigAction, EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion
from scanning_tool.state.signals import UI_ACTION_SIGNALS, region_committed, region_drafted


def test_edit_mode_service_drags_and_commits_capture_region() -> None:
    service = EditModeService()
    service.start()

    drafted = []
    committed = []
    config_payloads = []

    def collect_drafted(sender: object, active_region=None, draft_values=None, **kwargs: object) -> None:
        drafted.append((active_region, draft_values))

    def collect_committed(sender: object, active_region=None, draft_values=None, **kwargs: object) -> None:
        committed.append((active_region, draft_values))

    def capture_handler(sender: object, payload=None, **kwargs: object) -> None:
        config_payloads.append(payload)

    region_drafted.connect(collect_drafted, weak=False)
    region_committed.connect(collect_committed, weak=False)
    UI_ACTION_SIGNALS[ConfigAction.UPDATE_CAPTURE_REGION].connect(capture_handler, weak=False)

    UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].send(None)
    UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].send(None, left=100, top=120, width=300, height=200)
    UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].send(None)

    assert drafted[-1][0] == ActiveRegion.CAPTURE
    assert drafted[-1][1] == {"left": 100, "top": 120, "width": 300, "height": 200}
    assert committed[-1][0] == ActiveRegion.CAPTURE
    assert committed[-1][1] == {"left": 100, "top": 120, "width": 300, "height": 200}
    assert config_payloads == [{"left": 100, "top": 120, "width": 300, "height": 200}]

    service.stop()


def test_edit_mode_service_resets_draft_values() -> None:
    service = EditModeService()
    service.start()

    drafted = []

    def collect_drafted(sender: object, active_region=None, draft_values=None, **kwargs: object) -> None:
        drafted.append((active_region, draft_values))

    region_drafted.connect(collect_drafted, weak=False)

    UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].send(None)
    UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].send(None, left=80, top=90, width=200, height=150)
    UI_ACTION_SIGNALS[EditModeAction.RESET_REGION].send(None)

    assert drafted[-1][0] == ActiveRegion.CAPTURE
    assert drafted[-1][1] == {}

    service.stop()
