"""Service for managing the in-game edit mode."""

from __future__ import annotations

from typing import Any

from scanning_tool.services.base_service import BaseService
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion, EditModeReadModel
from scanning_tool.state.signals import UI_ACTION_SIGNALS
from scanning_tool.state.signals.edit_mode import edit_mode_changed, region_committed, region_drafted


class EditModeService(BaseService):
    def __init__(self) -> None:
        super().__init__()
        self._state = EditModeReadModel()

    def _on_start(self) -> None:
        UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].connect(self._on_enter_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.EXIT_EDIT_MODE].connect(self._on_exit_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].connect(self._on_drag_region)
        UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].connect(self._on_nudge_region)
        UI_ACTION_SIGNALS[EditModeAction.CYCLE_REGION].connect(self._on_cycle_region)
        UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].connect(self._on_commit_region)

    def _on_stop(self) -> None:
        UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].disconnect(self._on_enter_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.EXIT_EDIT_MODE].disconnect(self._on_exit_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].disconnect(self._on_drag_region)
        UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].disconnect(self._on_nudge_region)
        UI_ACTION_SIGNALS[EditModeAction.CYCLE_REGION].disconnect(self._on_cycle_region)
        UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].disconnect(self._on_commit_region)

    def _on_enter_edit_mode(self, sender: object) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=ActiveRegion.CAPTURE,
            toolbar_visible=True,
            draft_values={},
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_exit_edit_mode(self, sender: object) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=False,
            active_region=None,
            toolbar_visible=False,
            draft_values={},
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_drag_region(self, sender: object, **kwargs: Any) -> None:
        # TODO: Handle drag and publish region_drafted
        pass

    def _on_nudge_region(self, sender: object, **kwargs: Any) -> None:
        # TODO: Handle nudge and publish region_drafted
        pass

    def _on_cycle_region(self, sender: object) -> None:
        if not self._state.is_edit_mode:
            return
        
        regions = list(ActiveRegion)
        current_idx = regions.index(self._state.active_region) if self._state.active_region else -1
        next_idx = (current_idx + 1) % len(regions)
        next_region = regions[next_idx]
        
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=next_region,
            toolbar_visible=True,
            draft_values=self._state.draft_values,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_commit_region(self, sender: object) -> None:
        # TODO: Publish ConfigAction to persist region
        pass

edit_mode_service = EditModeService()

