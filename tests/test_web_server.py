from unittest.mock import MagicMock, patch

from flask import Flask

from scanning_tool.web.server import WebServer


def test_web_server_uses_waitress_when_available():
    app = MagicMock(spec=Flask)

    with patch("scanning_tool.web.server.serve") as mock_serve:
        WebServer.run(app, host="127.0.0.1", port=5000)

        mock_serve.assert_called_once_with(
            app,
            host="127.0.0.1",
            port=5000,
            _quiet=True,
        )
