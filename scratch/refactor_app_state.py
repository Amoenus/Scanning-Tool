import re
from pathlib import Path

replacements = [
    (r"from scanning_tool\.state import app_state", r"from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config"),
    (r"from scanning_tool\.state\.context import app_state", r"from scanning_tool.core.state_manager import config, scan_state, service_state, overlay_state, control_state, save_config"),
    (r"app_state\.settings\.capture\.cap_region\[\"left\"\]", r"config.capture_region.left"),
    (r"app_state\.settings\.capture\.cap_region\[\"top\"\]", r"config.capture_region.top"),
    (r"app_state\.settings\.capture\.cap_region\[\"width\"\]", r"config.capture_region.width"),
    (r"app_state\.settings\.capture\.cap_region\[\"height\"\]", r"config.capture_region.height"),
    (r"app_state\.settings\.capture\.cap_region\[\'left\'\]", r"config.capture_region.left"),
    (r"app_state\.settings\.capture\.cap_region\[\'top\'\]", r"config.capture_region.top"),
    (r"app_state\.settings\.capture\.cap_region\[\'width\'\]", r"config.capture_region.width"),
    (r"app_state\.settings\.capture\.cap_region\[\'height\'\]", r"config.capture_region.height"),
    
    (r"app_state\.settings\.anchor\.anchor_region\[\"left\"\]", r"config.anchor_template.left"),
    (r"app_state\.settings\.anchor\.anchor_region\[\"top\"\]", r"config.anchor_template.top"),
    (r"app_state\.settings\.anchor\.anchor_region\[\"width\"\]", r"config.anchor_template.width"),
    (r"app_state\.settings\.anchor\.anchor_region\[\"height\"\]", r"config.anchor_template.height"),
    (r"app_state\.settings\.anchor\.anchor_region\[\'left\'\]", r"config.anchor_template.left"),
    (r"app_state\.settings\.anchor\.anchor_region\[\'top\'\]", r"config.anchor_template.top"),
    (r"app_state\.settings\.anchor\.anchor_region\[\'width\'\]", r"config.anchor_template.width"),
    (r"app_state\.settings\.anchor\.anchor_region\[\'height\'\]", r"config.anchor_template.height"),
    
    (r"app_state\.settings\.anchor\.anchor_region", r"config.anchor_template"),
    (r"app_state\.settings\.capture\.cap_region", r"config.capture_region"),
    
    (r"app_state\.settings\.overlay\.label_color", r"config.overlay_config.label_color"),
    (r"app_state\.settings\.overlay\.info_overlay_offset", r"config.overlay_config.info_offset"),
    (r"app_state\.settings\.overlay\.debug_show_overlay", r"config.overlay_config.show_debug"),
    
    (r"app_state\.settings\.anchor\.auto_align_enabled", r"config.auto_alignment.enabled"),
    (r"app_state\.settings\.anchor\.anchor_template_dir", r"config.anchor_template_dir"),
    (r"app_state\.settings\.anchor\.anchor_threshold", r"config.anchor_threshold"),
    (r"app_state\.settings\.anchor\.anchor_offset", r"config.anchor_offset"),
    (r"app_state\.settings\.capture\.continuous_capture_interval", r"config.continuous_capture_interval"),
    
    (r"app_state\.settings\.ollama\.configured_ollama_host", r"config.ollama_config.host"),
    (r"app_state\.settings\.ollama\.default_ollama_host", r"config.ollama_config.default_host"),
    (r"app_state\.settings\.ollama\.ollama_model", r"config.ollama_config.model"),
    
    (r"app_state\.scan_state", r"scan_state"),
    (r"app_state\.service_state", r"service_state"),
    (r"app_state\.overlay_state", r"overlay_state"),
    (r"app_state\.control_state", r"control_state"),
    (r"app_state\.settings", r"config"),
    (r"lambda:\s*save_config\(app_state\)", r"save_config"),
]

def process(filepath):
    text = filepath.read_text("utf-8")
    original = text
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    if text != original:
        filepath.write_text(text, "utf-8")
        print(f"Updated {filepath.name}")

root_dir = Path("src/scanning_tool")
for p in root_dir.rglob("*.py"):
    path_str = str(p).replace("\\", "/")
    if "state/" in path_str or "domain/models" in path_str or "core/state_manager" in path_str:
        continue
    process(p)
