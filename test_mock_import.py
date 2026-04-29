import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("src"))

modules_to_mock = [
    "loguru",
    "cv2",
    "mss",
    "PIL",
    "ollama",
    "pydantic",
    "flask",
    "pynput",
    "pygetwindow",
    "pyautogui",
    "tkinter",
    "tkinter.ttk",
    "webbrowser",
    "mss.models",
]

patched_modules = {name: MagicMock() for name in modules_to_mock}
patcher = patch.dict(sys.modules, patched_modules)
patcher.start()

try:
    from scanning_tool.gui.tk.sections.mobile_overlay import MobileOverlaySection
    print("Successfully imported!")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    from scanning_tool.main import _start_web_server
    print("Successfully imported main!")
except Exception as e:
    import traceback
    traceback.print_exc()
