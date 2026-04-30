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
    print("Successfully imported!")
except Exception:
    import traceback
    traceback.print_exc()

try:
    print("Successfully imported main!")
except Exception:
    import traceback
    traceback.print_exc()
