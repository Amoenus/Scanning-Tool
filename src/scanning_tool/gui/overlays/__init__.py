"""Overlay API wrapper for backwards compatibility."""

from __future__ import annotations

from scanning_tool.gui.tk.overlays import *  # noqa: F401,F403
from scanning_tool.gui.tk.overlays import __all__ as __tk_all__

__all__ = __tk_all__
