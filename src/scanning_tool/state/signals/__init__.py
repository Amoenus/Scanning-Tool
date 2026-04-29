"""Application-wide event signals for the scanning tool."""

from blinker import Signal

from scanning_tool.gui.action_types import UiActionType
from scanning_tool.state.actions.scan import ScanAction

from scanning_tool.state.signals.runtime import (
    alignment_info_updated,
    ollama_readiness_changed,
    ollama_status_updated,
    status_updated,
)
from scanning_tool.state.signals.scan import (
    continuous_mode_changed,
    scan_completed,
    scan_failed,
    scan_started,
)

sync_capture_sliders_signal: Signal = Signal("sync_capture_sliders")
update_capture_overlay_region_signal: Signal = Signal("update_capture_overlay_region")
alignment_requested: Signal = Signal("alignment_requested")
alignment_failed: Signal = Signal("alignment_failed")
alignment_reset: Signal = Signal("alignment_reset")
alignment_applied_signal: Signal = Signal("alignment_applied")
scan_result_updated: Signal = Signal("scan_result_updated")
mobile_qr_ready: Signal = Signal("mobile_qr_ready")
ui_action: Signal = Signal("ui_action")

capture_overlay_root_changed: Signal = Signal("capture_overlay_root_changed")
info_overlay_root_changed: Signal = Signal("info_overlay_root_changed")
anchor_overlay_root_changed: Signal = Signal("anchor_overlay_root_changed")
anchor_overlay_visibility_changed: Signal = Signal("anchor_overlay_visibility_changed")
overlay_text_updated: Signal = Signal("overlay_text_updated")
show_border_changed: Signal = Signal("show_border_changed")

from scanning_tool.state.actions.runtime import RuntimeAction

UI_ACTION_SIGNALS: dict[object, Signal] = {
    action_type: Signal(f"ui_action_{action_type.value}")
    for enum_class in (UiActionType, ScanAction, RuntimeAction)
    for action_type in enum_class
}
