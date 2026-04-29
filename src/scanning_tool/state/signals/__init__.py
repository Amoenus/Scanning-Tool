"""Application-wide event signals for the scanning tool."""

from blinker import Signal

from scanning_tool.state.actions.config import ConfigAction
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.actions.event_log import EventLogAction
from scanning_tool.state.actions.runtime import RuntimeAction
from scanning_tool.state.actions.scan import ScanAction

from scanning_tool.state.signals.config import (
    anchor_overlay_root_changed,
    anchor_overlay_visibility_changed,
    capture_overlay_root_changed,
    info_overlay_root_changed,
    mobile_qr_ready,
    overlay_text_updated,
    show_border_changed,
    sync_capture_sliders_signal,
    update_capture_overlay_region_signal,
)
from scanning_tool.state.signals.runtime import (
    alignment_applied_signal,
    alignment_failed,
    alignment_info_updated,
    alignment_requested,
    alignment_reset,
    ollama_readiness_changed,
    ollama_status_updated,
    status_updated,
)
from scanning_tool.state.signals.scan import (
    continuous_mode_changed,
    scan_completed,
    scan_failed,
    scan_requested,
    scan_result_updated,
    scan_started,
)
from scanning_tool.state.signals.event_log import (
    event_log_emitted,
    raw_log_emitted,
)
from scanning_tool.state.signals.edit_mode import (
    edit_mode_changed,
    region_drafted,
    region_committed,
)

ui_action: Signal = Signal("ui_action")

UI_ACTION_SIGNALS: dict[object, Signal] = {
    action_type: Signal(f"ui_action_{action_type.value}")
    for enum_class in (ConfigAction, EditModeAction, EventLogAction, RuntimeAction, ScanAction)
    for action_type in enum_class
}
