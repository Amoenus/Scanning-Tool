from enum import StrEnum


class ConfigAction(StrEnum):
    """Actions for the Configuration concern."""

    UPDATE_CONTINUOUS_CAPTURE_INTERVAL = "update_continuous_capture_interval"
    SAVE_CONFIG = "save_config"
    OPEN_MOBILE_UI = "open_mobile_ui"
    SHOW_MOBILE_QR = "show_mobile_qr"
    APPLY_OLLAMA_MODEL = "apply_ollama_model"
    APPLY_OLLAMA_HOST = "apply_ollama_host"
    USE_LOCALHOST = "use_localhost"
    TOGGLE_AUTO_ALIGNMENT = "toggle_auto_alignment"
    TOGGLE_ANCHOR_OVERLAY = "toggle_anchor_overlay"
    UPDATE_ALIGNMENT_POLL_INTERVAL = "update_alignment_poll_interval"
    UPDATE_ANCHOR_THRESHOLD = "update_anchor_threshold"
    UPDATE_ANCHOR_REGION = "update_anchor_region"
    UPDATE_ANCHOR_OFFSET = "update_anchor_offset"
    RELOAD_ANCHOR_TEMPLATES = "reload_anchor_templates"
    OPEN_ANCHOR_DIRECTORY = "open_anchor_directory"
    UPDATE_CAPTURE_REGION = "update_capture_region"
    TOGGLE_CAPTURE_BOX = "toggle_capture_box"
    TOGGLE_CAPTURE_BORDER = "toggle_capture_border"
    UPDATE_OVERLAY_REGION = "update_overlay_region"
    CHOOSE_LABEL_COLOR = "choose_label_color"
    UPDATE_RESULT_DISPLAY_OFFSET = "update_result_display_offset"
