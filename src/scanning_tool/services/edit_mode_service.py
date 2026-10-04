"""Service for managing the in-game edit mode."""

from __future__ import annotations

import pydantic
from typing import Any

from scanning_tool.gui.dtos import RegionDragPayload, RegionNudgePayload, RegionSelectPayload
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
        self._pending_region_payloads: dict[ActiveRegion, dict[str, int]] = {}

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
            original_region_payload=self._capture_original_region_payloads(),
        )
        self._pending_region_payloads = self._capture_original_region_payloads()
        edit_mode_changed.send(self, state=self._state)

    def _on_exit_edit_mode(self, sender: object, **kwargs: Any) -> None:
        self._state = EditModeReadModel(
            is_edit_mode=False,
            active_region=None,
            toolbar_visible=False,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_drag_region(
        self,
        sender: object,
        payload: RegionDragPayload | dict[str, object] | None = None,
        **kwargs: Any,
    ) -> None:
        if not self._state.is_edit_mode:
            return

        merged_payload = dict((payload or {}) if isinstance(payload, dict) else (payload.model_dump() if payload else {}))
        merged_payload.update(kwargs)

        try:
            data = RegionDragPayload.model_validate(merged_payload)
        except pydantic.ValidationError:
            return

        # check if it is completely empty
        if all(v is None for v in data.model_dump().values()):
            return

        full_payload = self._payload_for_region(
            self._state.active_region or ActiveRegion.CAPTURE,
            data,
        )
        if self._state.active_region is not None:
            self._pending_region_payloads[self._state.active_region] = full_payload
        self._publish_region_config_action(self._state.active_region, full_payload)
        edit_mode_changed.send(self, state=self._state)

    def _on_nudge_region(
        self,
        sender: object,
        payload: RegionNudgePayload | dict[str, object] | None = None,
        **kwargs: Any,
    ) -> None:
        if not self._state.is_edit_mode:
            return

        merged_payload = dict((payload or {}) if isinstance(payload, dict) else (payload.model_dump() if payload else {}))
        merged_payload.update(kwargs)

        try:
            data = RegionNudgePayload.model_validate(merged_payload)
        except pydantic.ValidationError:
            return

        # check if it is completely empty
        if all(v is None for v in data.model_dump().values()):
            return

        full_payload = self._payload_for_region(
            self._state.active_region or ActiveRegion.CAPTURE,
            data,
        )
        if self._state.active_region is not None:
            self._pending_region_payloads[self._state.active_region] = full_payload
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
            original_region_payload=self._state.original_region_payload,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_commit_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        final_payload = self._pending_region_payloads.get(
            self._state.active_region,
            self._payload_for_region(self._state.active_region, None),
        )
        self._publish_region_config_action(self._state.active_region, final_payload)
        region_committed.send(self, active_region=self._state.active_region)

    def _on_select_region(
        self,
        sender: object,
        payload: RegionSelectPayload | dict[str, object] | None = None,
        **kwargs: Any,
    ) -> None:
        if not self._state.is_edit_mode:
            return

        merged_payload = dict((payload or {}) if isinstance(payload, dict) else (payload.model_dump() if payload else {}))
        merged_payload.update(kwargs)

        try:
            data = RegionSelectPayload.model_validate(merged_payload)
        except pydantic.ValidationError:
            return

        region_name = data.region
        if region_name is None:
            return

        try:
            active_region = ActiveRegion(region_name)
        except ValueError:
            return

        self._state = EditModeReadModel(
            is_edit_mode=True,
            active_region=active_region,
            toolbar_visible=True,
            original_region_payload=self._state.original_region_payload,
        )
        edit_mode_changed.send(self, state=self._state)

    def _on_reset_region(self, sender: object, **kwargs: Any) -> None:
        if not self._state.is_edit_mode or not self._state.active_region:
            return

        original_payload = self._state.original_region_payload.get(self._state.active_region)
        if not original_payload:
            return

        self._pending_region_payloads[self._state.active_region] = original_payload
        self._publish_region_config_action(self._state.active_region, original_payload)
        edit_mode_changed.send(self, state=self._state)

    def _payload_for_region(self, region: ActiveRegion, payload: RegionDragPayload | RegionNudgePayload | None) -> dict[str, int]:

        def _val(val: float | int | None, fallback: float | int) -> float | int:
            return val if val is not None else fallback

        if region == ActiveRegion.CAPTURE or region == ActiveRegion.ANCHOR:
            source = manager.config.capture_region if region == ActiveRegion.CAPTURE else manager.config.anchor_template
            if isinstance(payload, RegionDragPayload):
                left = int(_val(payload.left, source.left))
                top = int(_val(payload.top, source.top))
                width = int(_val(payload.width, source.width))
                height = int(_val(payload.height, source.height))
                return {"left": left, "top": top, "width": max(1, width), "height": max(1, height)}
            elif isinstance(payload, RegionNudgePayload):
                left = int(source.left) + int(_val(payload.delta_left, 0))
                top = int(source.top) + int(_val(payload.delta_top, 0))
                width = int(source.width) + int(_val(payload.delta_width, 0))
                height = int(source.height) + int(_val(payload.delta_height, 0))
                return {"left": left, "top": top, "width": max(1, width), "height": max(1, height)}
            else:
                return {"left": int(source.left), "top": int(source.top), "width": int(source.width), "height": int(source.height)}

        if region == ActiveRegion.INFO:
            info_source = manager.config.overlay_config.info_offset
            if isinstance(payload, RegionDragPayload):
                x = int(_val(payload.x, info_source.x))
                y = int(_val(payload.y, info_source.y))
                return {"x": x, "y": y}
            elif isinstance(payload, RegionNudgePayload):
                delta_x = _val(payload.delta_x, _val(payload.delta_left, 0))
                delta_y = _val(payload.delta_y, _val(payload.delta_top, 0))
                x = int(info_source.x) + int(delta_x)
                y = int(info_source.y) + int(delta_y)
                return {"x": x, "y": y}
            else:
                return {"x": int(info_source.x), "y": int(info_source.y)}

        return {}

    def _capture_original_region_payloads(self) -> dict[ActiveRegion, dict[str, int]]:
        capture_region = manager.config.capture_region
        anchor_template = manager.config.anchor_template
        info_offset = manager.config.overlay_config.info_offset
        return {
            ActiveRegion.CAPTURE: {
                "left": int(capture_region.left),
                "top": int(capture_region.top),
                "width": int(capture_region.width),
                "height": int(capture_region.height),
            },
            ActiveRegion.ANCHOR: {
                "left": int(anchor_template.left),
                "top": int(anchor_template.top),
                "width": int(anchor_template.width),
                "height": int(anchor_template.height),
            },
            ActiveRegion.INFO: {
                "x": int(info_offset.x),
                "y": int(info_offset.y),
            },
        }

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
