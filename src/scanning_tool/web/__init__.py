"""Web overlay package for the scanning tool."""

from scanning_tool.web.app import WebService, create_app, get_local_ip
from scanning_tool.web.server import WebServer
from scanning_tool.state.manifest import ConcernManifest
from scanning_tool.state.signals.scan import scan_completed

MANIFEST = ConcernManifest(
    claimed_concerns=frozenset({"scan_result"}),
    published_actions=frozenset(),
    subscribed_signals=frozenset({scan_completed}),
)

__all__ = ["WebServer", "WebService", "create_app", "get_local_ip", "MANIFEST"]
