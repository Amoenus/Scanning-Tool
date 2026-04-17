import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to sys.path
sys.path.append(os.path.abspath("src"))

# Mock all dependencies that are missing in the environment
modules_to_mock = [
    "loguru",
    "numpy",
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
    "scanning_tool.deposits",
    "scanning_tool.gui.app",
    "scanning_tool.hotkeys",
    "scanning_tool.logging_setup",
    "scanning_tool.ollama",
    "scanning_tool.services.alignment_service",
    "scanning_tool.services.ollama_service",
    "scanning_tool.core.anchor",
    "scanning_tool.web"
]

for module_name in modules_to_mock:
    sys.modules[module_name] = MagicMock()

# Mocking state_manager
class MockConfig:
    def __init__(self):
        self.web_server_config = MagicMock()
        self.web_server_config.host = "0.0.0.0"
        self.web_server_config.port = 5000

mock_state_manager = MagicMock()
mock_state_manager.config = MockConfig()
sys.modules["scanning_tool.core.state_manager"] = mock_state_manager

class TestSecurity(unittest.TestCase):
    def setUp(self):
        # Reset defaults before each test
        mock_state_manager.config.web_server_config.host = "0.0.0.0"
        mock_state_manager.config.web_server_config.port = 5000

    def test_flask_binding_default(self):
        with patch("scanning_tool.main.create_app") as mock_create_app:
            with patch("scanning_tool.main.Thread") as mock_thread:
                with patch("scanning_tool.main.logger") as mock_logger:
                    with patch("scanning_tool.main.get_local_ip") as mock_get_local_ip:
                        mock_get_local_ip.return_value = "192.168.1.100"
                        from scanning_tool.main import _start_web_server

                        mock_flask_app = MagicMock()
                        mock_create_app.return_value = mock_flask_app

                        _start_web_server()

                        self.assertTrue(mock_thread.called)
                        args, kwargs = mock_thread.call_args
                        target = kwargs.get('target') or args[0]
                        target()

                        mock_flask_app.run.assert_called_once_with(host="0.0.0.0", port=5000, debug=False)

                        mock_logger.info.assert_called_once()
                        msg = mock_logger.info.call_args[0][0]
                        self.assertIn("192.168.1.100", msg)

    def test_flask_binding_custom(self):
        mock_state_manager.config.web_server_config.host = "127.0.0.1"
        mock_state_manager.config.web_server_config.port = 8080

        with patch("scanning_tool.main.create_app") as mock_create_app:
            with patch("scanning_tool.main.Thread") as mock_thread:
                with patch("scanning_tool.main.logger") as mock_logger:
                    from scanning_tool.main import _start_web_server

                    mock_flask_app = MagicMock()
                    mock_create_app.return_value = mock_flask_app

                    _start_web_server()

                    args, kwargs = mock_thread.call_args
                    target = kwargs.get('target') or args[0]
                    target()

                    mock_flask_app.run.assert_called_once_with(host="127.0.0.1", port=8080, debug=False)

                    mock_logger.info.assert_called_once_with("Starting overlay server: http://127.0.0.1:8080")

    def test_mobile_overlay_url_default(self):
        # Already set to 0.0.0.0 in setUp
        with patch("scanning_tool.gui.sections.ollama.webbrowser") as mock_webbrowser:
            with patch("scanning_tool.gui.sections.ollama.get_local_ip") as mock_get_local_ip:
                mock_get_local_ip.return_value = "192.168.1.100"
                from scanning_tool.gui.sections.ollama import OllamaSection

                section = OllamaSection()
                section._status = MagicMock()
                section._open_mobile_overlay()

                mock_webbrowser.open_new_tab.assert_called_once_with("http://192.168.1.100:5000")

    def test_mobile_overlay_url_custom(self):
        mock_state_manager.config.web_server_config.host = "127.0.0.1"
        mock_state_manager.config.web_server_config.port = 8080

        with patch("scanning_tool.gui.sections.ollama.webbrowser") as mock_webbrowser:
            from scanning_tool.gui.sections.ollama import OllamaSection

            section = OllamaSection()
            section._status = MagicMock()
            section._open_mobile_overlay()

            mock_webbrowser.open_new_tab.assert_called_once_with("http://127.0.0.1:8080")

if __name__ == "__main__":
    unittest.main()
