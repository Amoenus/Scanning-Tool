from __future__ import annotations

from dataclasses import dataclass, field

from scanning_tool.state.actions import ActionType
from scanning_tool.state.signals import UI_ACTION_SIGNALS, ui_action

type UiActionPayload = dict[str, object]


def _empty_payload() -> UiActionPayload:
    return {}


@dataclass(frozen=True)
class UiAction:
    """Represents a user intent event emitted from the GUI."""

    type: ActionType
    payload: UiActionPayload = field(default_factory=_empty_payload)


def publish_ui_action(action_type: ActionType, payload: UiActionPayload | None = None) -> None:
    normalized_payload: UiActionPayload = payload if payload is not None else {}
    ui_action.send(None, action=UiAction(type=action_type, payload=normalized_payload))

    signal = UI_ACTION_SIGNALS.get(action_type)
    if signal is not None:
        signal.send(None, payload=normalized_payload)
