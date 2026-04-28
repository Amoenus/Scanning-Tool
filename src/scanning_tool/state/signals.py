"""Application-wide event signals for the scanning tool."""

from blinker import Signal

status_updated: Signal = Signal("status_updated")
sync_capture_sliders_signal: Signal = Signal("sync_capture_sliders")
update_capture_overlay_region_signal: Signal = Signal("update_capture_overlay_region")
alignment_applied_signal: Signal = Signal("alignment_applied")
ollama_status_updated: Signal = Signal("ollama_status_updated")
ollama_readiness_changed: Signal = Signal("ollama_readiness_changed")
mobile_qr_ready: Signal = Signal("mobile_qr_ready")
ui_action: Signal = Signal("ui_action")

ui_action_single_scan: Signal = Signal("ui_action_single_scan")
ui_action_toggle_continuous_capture: Signal = Signal("ui_action_toggle_continuous_capture")
ui_action_update_continuous_capture_interval: Signal = Signal("ui_action_update_continuous_capture_interval")
ui_action_save_config: Signal = Signal("ui_action_save_config")
ui_action_open_mobile_ui: Signal = Signal("ui_action_open_mobile_ui")
ui_action_show_mobile_qr: Signal = Signal("ui_action_show_mobile_qr")
ui_action_apply_ollama_model: Signal = Signal("ui_action_apply_ollama_model")
ui_action_apply_ollama_host: Signal = Signal("ui_action_apply_ollama_host")
ui_action_use_localhost: Signal = Signal("ui_action_use_localhost")
ui_action_restart_ollama: Signal = Signal("ui_action_restart_ollama")
ui_action_toggle_auto_alignment: Signal = Signal("ui_action_toggle_auto_alignment")
ui_action_toggle_anchor_overlay: Signal = Signal("ui_action_toggle_anchor_overlay")
ui_action_update_alignment_poll_interval: Signal = Signal("ui_action_update_alignment_poll_interval")
ui_action_update_anchor_threshold: Signal = Signal("ui_action_update_anchor_threshold")
ui_action_update_anchor_region: Signal = Signal("ui_action_update_anchor_region")
ui_action_update_anchor_offset: Signal = Signal("ui_action_update_anchor_offset")
ui_action_reload_anchor_templates: Signal = Signal("ui_action_reload_anchor_templates")
ui_action_manual_realign: Signal = Signal("ui_action_manual_realign")
ui_action_open_anchor_directory: Signal = Signal("ui_action_open_anchor_directory")
ui_action_update_capture_region: Signal = Signal("ui_action_update_capture_region")
ui_action_toggle_capture_box: Signal = Signal("ui_action_toggle_capture_box")
ui_action_toggle_capture_border: Signal = Signal("ui_action_toggle_capture_border")
ui_action_update_result_display_offset: Signal = Signal("ui_action_update_result_display_offset")

UI_ACTION_SIGNALS: dict[str, Signal] = {
    "single_scan": ui_action_single_scan,
    "toggle_continuous_capture": ui_action_toggle_continuous_capture,
    "update_continuous_capture_interval": ui_action_update_continuous_capture_interval,
    "save_config": ui_action_save_config,
    "open_mobile_ui": ui_action_open_mobile_ui,
    "show_mobile_qr": ui_action_show_mobile_qr,
    "apply_ollama_model": ui_action_apply_ollama_model,
    "apply_ollama_host": ui_action_apply_ollama_host,
    "use_localhost": ui_action_use_localhost,
    "restart_ollama": ui_action_restart_ollama,
    "toggle_auto_alignment": ui_action_toggle_auto_alignment,
    "toggle_anchor_overlay": ui_action_toggle_anchor_overlay,
    "update_alignment_poll_interval": ui_action_update_alignment_poll_interval,
    "update_anchor_threshold": ui_action_update_anchor_threshold,
    "update_anchor_region": ui_action_update_anchor_region,
    "update_anchor_offset": ui_action_update_anchor_offset,
    "reload_anchor_templates": ui_action_reload_anchor_templates,
    "manual_realign": ui_action_manual_realign,
    "open_anchor_directory": ui_action_open_anchor_directory,
    "update_capture_region": ui_action_update_capture_region,
    "toggle_capture_box": ui_action_toggle_capture_box,
    "toggle_capture_border": ui_action_toggle_capture_border,
    "update_result_display_offset": ui_action_update_result_display_offset,
}
