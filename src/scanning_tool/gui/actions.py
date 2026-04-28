from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scanning_tool.state.signals import UI_ACTION_SIGNALS, ui_action


@dataclass(frozen=True)
class UiAction:
    """Represents a user intent event emitted from the GUI."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)


class UiActionType:
    SINGLE_SCAN = "single_scan"
    TOGGLE_CONTINUOUS_CAPTURE = "toggle_continuous_capture"
    UPDATE_CONTINUOUS_CAPTURE_INTERVAL = "update_continuous_capture_interval"
    SAVE_CONFIG = "save_config"
    OPEN_MOBILE_UI = "open_mobile_ui"
    SHOW_MOBILE_QR = "show_mobile_qr"
    APPLY_OLLAMA_MODEL = "apply_ollama_model"
    APPLY_OLLAMA_HOST = "apply_ollama_host"
    USE_LOCALHOST = "use_localhost"
    RESTART_OLLAMA = "restart_ollama"
    TOGGLE_AUTO_ALIGNMENT = "toggle_auto_alignment"
    TOGGLE_ANCHOR_OVERLAY = "toggle_anchor_overlay"
    UPDATE_ALIGNMENT_POLL_INTERVAL = "update_alignment_poll_interval"
    UPDATE_ANCHOR_THRESHOLD = "update_anchor_threshold"
    UPDATE_ANCHOR_REGION = "update_anchor_region"
    UPDATE_ANCHOR_OFFSET = "update_anchor_offset"
    RELOAD_ANCHOR_TEMPLATES = "reload_anchor_templates"
    MANUAL_REALIGN = "manual_realign"
    OPEN_ANCHOR_DIRECTORY = "open_anchor_directory"
    UPDATE_CAPTURE_REGION = "update_capture_region"
    TOGGLE_CAPTURE_BOX = "toggle_capture_box"
    TOGGLE_CAPTURE_BORDER = "toggle_capture_border"
    UPDATE_RESULT_DISPLAY_OFFSET = "update_result_display_offset"


def publish_ui_action(type: str, payload: dict[str, Any] | None = None) -> None:
    payload = payload or {}
    ui_action.send(None, action=UiAction(type=type, payload=payload))

    signal = UI_ACTION_SIGNALS.get(type)
    if signal is not None:
        signal.send(None, payload=payload)
