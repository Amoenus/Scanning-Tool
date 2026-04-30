"""Service for managing the in-game edit mode."""

from __future__ import annotations

from typing import Any

from scanning_tool.services.base_service import BaseService
from scanning_tool.state import manager
from scanning_tool.state.actions.config import ConfigAction
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion, EditModeReadModel
from scanning_tool.state.signals import UI_ACTION_SIGNALS
from scanning_tool.state.signals.edit_mode import edit_mode_changed, region_committed, region_drafted


class EditModeService(BaseService):
    def __init__(self) -> None:
        super().__init__()
        self._state = EditModeReadModel()

    @property
    def state(self) -> EditModeReadModel:
        return self._state

    def _on_start(self) -> None:
        UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].connect(self._on_enter_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.EXIT_EDIT_MODE].connect(self._on_exit_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.SELECT_REGION].connect(self._on_select_region)
        UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].connect(self._on_drag_region)
        UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].connect(self._on_nudge_region)
        UI_ACTION_SIGNALS[EditModeAction.RESET_REGION].connect(self._on_reset_region)
        UI_ACTION_SIGNALS[EditModeAction.CYCLE_REGION].connect(self._on_cycle_region)
        UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].connect(self._on_commit_region)

    def _on_stop(self) -> None:
        UI_ACTION_SIGNALS[EditModeAction.ENTER_EDIT_MODE].disconnect(self._on_enter_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.EXIT_EDIT_MODE].disconnect(self._on_exit_edit_mode)
        UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].disconnect(self._on_drag_region)
        UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].disconnect(self._on_nudge_region)
        UI_ACTION_SIGNALS[EditModeAction.CYCLE_REGION].disconnect(self._on_cycle_region)
        UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].disconnect(self._on_commit_region)

    def _on_enter_edit_mode(self, sender: object, **kwargs: Any) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=ActiveRegion.CAPTURE,
            toolbar_visible=True,
            draft_values={},
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_exit_edit_mode(self, sender: object, **kwargs: Any) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=False,
            active_region=None,
            toolbar_visible=False,
            draft_values={},
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_drag_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode:
            return

        payload = {k: int(v) for k, v in kwargs.items() if isinstance(v, int) or isinstance(v, float)}
        if not payload:
            return

        draft_values = self._merge_draft_values(payload)
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=self._state.active_region or ActiveRegion.CAPTURE,
            toolbar_visible=True,
            draft_values=draft_values,
        )
        region_drafted.send(self, active_region=self._state.active_region, draft_values=draft_values)
        edit_mode_changed.send(self, state=self._state)
        self._publish_region_config_action(self._state.active_region, draft_values)

    def _on_nudge_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode:
            return

        draft_values = self._state.draft_values.copy()
        delta_values: dict[str, int] = {}
        for field_name, value in kwargs.items():
            if not isinstance(value, (int, float)):
                continue
            if field_name.startswith("delta_"):
                target_field = field_name[len("delta_"):]
                if target_field in draft_values:
                    current = int(draft_values[target_field])
                else:
                    current = self._current_region_field_value(target_field)
                delta_values[target_field] = current + int(value)
            else:
                delta_values[field_name] = int(value)

        if not delta_values:
            return

        merged_values = self._merge_draft_values(delta_values)
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=self._state.active_region or ActiveRegion.CAPTURE,
            toolbar_visible=True,
            draft_values=merged_values,
        )
        region_drafted.send(self, active_region=self._state.active_region, draft_values=merged_values)
        edit_mode_changed.send(self, state=self._state)
        self._publish_region_config_action(self._state.active_region, merged_values)

    def _on_cycle_region(self, sender: object, **kwargs: Any) -> None:
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

    def _on_commit_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        payload = self._payload_for_region(self._state.active_region, self._state.draft_values)
        if payload:
            config_action = self._config_action_for_region(self._state.active_region)
            signal = UI_ACTION_SIGNALS.get(config_action)
            if signal is not None:
                signal.send(self, payload=payload)

        region_committed.send(self, active_region=self._state.active_region, draft_values=self._state.draft_values)

    def _on_select_region(self, sender: object, region: str | None = None, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not region:
            return

        try:
            active_region = ActiveRegion(region)
        except ValueError:
            return

        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=active_region,
            toolbar_visible=True,
            draft_values=self._state.draft_values,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_reset_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        draft_values = self._state.draft_values.copy()
        if self._state.active_region in (ActiveRegion.CAPTURE, ActiveRegion.ANCHOR):
            for key in ("left", "top", "width", "height"):
                draft_values.pop(key, None)
        else:
            for key in ("x", "y"):
                draft_values.pop(key, None)

        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=self._state.active_region,
            toolbar_visible=True,
            draft_values=draft_values,
        )
        region_drafted.send(self, active_region=self._state.active_region, draft_values=draft_values)
        edit_mode_changed.send(self, state=self._state)

    def _merge_draft_values(self, payload: dict[str, int]) -> dict[str, int]:
        merged = self._state.draft_values.copy()
        merged.update(payload)
        return merged

    def _payload_for_region(self, region: ActiveRegion, draft_values: dict[str, int]) -> dict[str, int]:
        if region == ActiveRegion.CAPTURE or region == ActiveRegion.ANCHOR:
            return {
                k: int(draft_values[k])
                for k in ("left", "top", "width", "height")
                if k in draft_values
            }
        if region == ActiveRegion.INFO:
            return {
                k: int(draft_values[k])
                for k in ("x", "y")
                if k in draft_values
            }
        return {}

    def _current_region_field_value(self, field_name: str) -> int:
        if self._state.active_region == ActiveRegion.CAPTURE:
            region = manager.config.capture_region
            return int(getattr(region, field_name, 0))
        if self._state.active_region == ActiveRegion.ANCHOR:
            region = manager.config.anchor_template
            return int(getattr(region, field_name, 0))
        if self._state.active_region == ActiveRegion.INFO:
            offset = manager.config.overlay_config.info_offset
            return int(getattr(offset, field_name, 0))
        return 0

    def _publish_region_config_action(
        self,
        active_region: ActiveRegion | None,
        draft_values: dict[str, int],
    ) -> None:
        if active_region is None:
            return

        payload = self._payload_for_region(active_region, draft_values)
        if not payload:
            return

        config_action = self._config_action_for_region(active_region)
        signal = UI_ACTION_SIGNALS.get(config_action)
        if signal is not None:
            signal.send(self, payload=payload)

    def _config_action_for_region(self, region: ActiveRegion) -> ConfigAction:
        if region == ActiveRegion.CAPTURE:
            return ConfigAction.UPDATE_CAPTURE_REGION
        if region == ActiveRegion.ANCHOR:
            return ConfigAction.UPDATE_ANCHOR_REGION
        return ConfigAction.UPDATE_RESULT_DISPLAY_OFFSET

edit_mode_service = EditModeService()

