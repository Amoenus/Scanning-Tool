"""Service for managing the in-game edit mode."""

from __future__ import annotations

from typing import Any

from scanning_tool.services.base_service import BaseService
from scanning_tool.state import manager
from scanning_tool.state.actions.config import ConfigAction
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion, EditModeReadModel
from scanning_tool.state.signals import UI_ACTION_SIGNALS
from scanning_tool.state.signals.edit_mode import edit_mode_changed, region_committed


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
        UI_ACTION_SIGNALS[EditModeAction.SELECT_REGION].disconnect(self._on_select_region)
        UI_ACTION_SIGNALS[EditModeAction.DRAG_REGION].disconnect(self._on_drag_region)
        UI_ACTION_SIGNALS[EditModeAction.NUDGE_REGION].disconnect(self._on_nudge_region)
        UI_ACTION_SIGNALS[EditModeAction.RESET_REGION].disconnect(self._on_reset_region)
        UI_ACTION_SIGNALS[EditModeAction.CYCLE_REGION].disconnect(self._on_cycle_region)
        UI_ACTION_SIGNALS[EditModeAction.COMMIT_REGION].disconnect(self._on_commit_region)

    def _on_enter_edit_mode(self, sender: object, **kwargs: Any) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=ActiveRegion.CAPTURE,
            toolbar_visible=True,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_exit_edit_mode(self, sender: object, **kwargs: Any) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=False,
            active_region=None,
            toolbar_visible=False,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_drag_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode:
            return

        payload = {k: int(v) for k, v in kwargs.items() if isinstance(v, int) or isinstance(v, float)}
        if not payload:
            return

        full_payload = self._payload_for_region(self._state.active_region or ActiveRegion.CAPTURE, payload)
        self._publish_region_config_action(self._state.active_region, full_payload)
        edit_mode_changed.send(self, state=self._state)

    def _on_nudge_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode:
            return

        payload = {k: int(v) for k, v in kwargs.items() if isinstance(v, int) or isinstance(v, float)}
        if not payload:
            return

        full_payload = self._payload_for_region(self._state.active_region or ActiveRegion.CAPTURE, payload)
        self._publish_region_config_action(self._state.active_region, full_payload)
        edit_mode_changed.send(self, state=self._state)

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
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_commit_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        region_committed.send(self, active_region=self._state.active_region)

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
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_reset_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        edit_mode_changed.send(self, state=self._state)

    def _payload_for_region(self, region: ActiveRegion, payload: dict[str, int]) -> dict[str, int]:
        if region == ActiveRegion.CAPTURE or region == ActiveRegion.ANCHOR:
            source = (
                manager.config.capture_region
                if region == ActiveRegion.CAPTURE
                else manager.config.anchor_template
            )
            left = int(payload.get("left", source.left)) + int(payload.get("delta_left", 0))
            top = int(payload.get("top", source.top)) + int(payload.get("delta_top", 0))
            width = int(payload.get("width", source.width)) + int(payload.get("delta_width", 0))
            height = int(payload.get("height", source.height)) + int(payload.get("delta_height", 0))
            return {"left": left, "top": top, "width": max(1, width), "height": max(1, height)}

        if region == ActiveRegion.INFO:
            source = manager.config.overlay_config.info_offset
            x = int(payload.get("x", source.x)) + int(payload.get("delta_x", payload.get("delta_left", 0)))
            y = int(payload.get("y", source.y)) + int(payload.get("delta_y", payload.get("delta_top", 0)))
            return {"x": x, "y": y}

        return {}

    def _publish_region_config_action(
        self,
        active_region: ActiveRegion | None,
        payload: dict[str, int],
    ) -> None:
        if active_region is None:
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

