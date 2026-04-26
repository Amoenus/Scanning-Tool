import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to sys.path so local source packages are importable.
sys.path.insert(0, os.path.abspath("src"))

# Mock only external dependencies that may not be installed in the test environment.
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
]


def _create_mocked_modules():
    return {module_name: MagicMock() for module_name in modules_to_mock}


# Mocking state_manager
class MockConfig:
    def __init__(self):
        self.web_server_config = MagicMock()
        self.web_server_config.host = "0.0.0.0"
        self.web_server_config.port = 5000


class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.mock_state_manager = MagicMock()
        self.mock_state_manager.config = MockConfig()

        patched_modules = _create_mocked_modules()
        patched_modules["scanning_tool.state.manager"] = self.mock_state_manager
        self._patcher = patch.dict(sys.modules, patched_modules)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()


    def test_flask_binding_default(self):
        with patch("scanning_tool.web.app.WebService.create_app") as mock_create_app:
            with patch("scanning_tool.main.Thread") as mock_thread:
                with patch("scanning_tool.main.logger") as mock_logger:
                    with patch("scanning_tool.main.get_local_ip") as mock_get_local_ip:
                        with patch("scanning_tool.web.server.WebServer.run") as mock_web_run:
                            mock_get_local_ip.return_value = "192.168.1.100"
                            from scanning_tool.main import _start_web_server

                            mock_flask_app = MagicMock()
                            mock_create_app.return_value = mock_flask_app

                            _start_web_server(
                                config=self.mock_state_manager.config,
                                scan_state=MagicMock(),
                                service_state=MagicMock(),
                            )

                            self.assertTrue(mock_thread.called)
                            args, kwargs = mock_thread.call_args
                            target = kwargs.get("target") or args[0]
                            target()

                            mock_web_run.assert_called_once_with(
                                mock_flask_app,
                                host="0.0.0.0",
                                port=5000,
                            )

                            mock_logger.info.assert_called_once()
                            msg = mock_logger.info.call_args[0][0]
                            self.assertIn("192.168.1.100", msg)

    def test_flask_binding_custom(self):
        self.mock_state_manager.config.web_server_config.host = "127.0.0.1"
        self.mock_state_manager.config.web_server_config.port = 8080

        with patch("scanning_tool.web.app.WebService.create_app") as mock_create_app:
            with patch("scanning_tool.main.Thread") as mock_thread:
                with patch("scanning_tool.main.logger") as mock_logger:
                    with patch("scanning_tool.web.server.WebServer.run") as mock_web_run:
                        from scanning_tool.main import _start_web_server

                        mock_flask_app = MagicMock()
                        mock_create_app.return_value = mock_flask_app

                        _start_web_server(
                            config=self.mock_state_manager.config,
                            scan_state=MagicMock(),
                            service_state=MagicMock(),
                        )

                        args, kwargs = mock_thread.call_args
                        target = kwargs.get("target") or args[0]
                        target()

                        mock_web_run.assert_called_once_with(
                            mock_flask_app,
                            host="127.0.0.1",
                            port=8080,
                        )

                        mock_logger.info.assert_called_once_with(
                            "Starting overlay server: http://127.0.0.1:8080"
                        )

    def test_mobile_overlay_url_default(self):
        # Already set to 0.0.0.0 in setUp
        with patch("scanning_tool.gui.tk.sections.ollama.webbrowser") as mock_webbrowser:
            with patch(
                "scanning_tool.gui.tk.sections.ollama.get_local_ip"
            ) as mock_get_local_ip:
                mock_get_local_ip.return_value = "192.168.1.100"
                from scanning_tool.gui.tk.sections.ollama import OllamaSection

                section = OllamaSection()
                section._status = MagicMock()
                section._open_mobile_overlay()

                mock_webbrowser.open_new_tab.assert_called_once_with(
                    "http://192.168.1.100:5000"
                )

    def test_mobile_overlay_url_custom(self):
        self.mock_state_manager.config.web_server_config.host = "127.0.0.1"
        self.mock_state_manager.config.web_server_config.port = 8080

        with patch("scanning_tool.gui.tk.sections.ollama.webbrowser") as mock_webbrowser:
            from scanning_tool.gui.tk.sections.ollama import OllamaSection

            section = OllamaSection()
            section._status = MagicMock()
            section._open_mobile_overlay()

            mock_webbrowser.open_new_tab.assert_called_once_with(
                "http://127.0.0.1:8080"
            )


if __name__ == "__main__":
    unittest.main()
