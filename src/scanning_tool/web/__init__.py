"""Web overlay package for the scanning tool."""

from scanning_tool.web.app import WebService, create_app, get_local_ip

__all__ = ["WebService", "create_app", "get_local_ip"]
