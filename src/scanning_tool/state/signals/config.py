from blinker import Signal

sync_capture_sliders_signal: Signal = Signal("sync_capture_sliders")
update_capture_overlay_region_signal: Signal = Signal("update_capture_overlay_region")
capture_overlay_root_changed: Signal = Signal("capture_overlay_root_changed")
info_overlay_root_changed: Signal = Signal("info_overlay_root_changed")
anchor_overlay_root_changed: Signal = Signal("anchor_overlay_root_changed")
anchor_overlay_visibility_changed: Signal = Signal("anchor_overlay_visibility_changed")
overlay_text_updated: Signal = Signal("overlay_text_updated")
show_border_changed: Signal = Signal("show_border_changed")
mobile_qr_ready: Signal = Signal("mobile_qr_ready")

__all__ = [
    "anchor_overlay_root_changed",
    "anchor_overlay_visibility_changed",
    "capture_overlay_root_changed",
    "info_overlay_root_changed",
    "mobile_qr_ready",
    "overlay_text_updated",
    "show_border_changed",
    "sync_capture_sliders_signal",
    "update_capture_overlay_region_signal",
]
