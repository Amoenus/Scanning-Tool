"""Tkinter GUI wrapper module for backwards compatibility."""

from __future__ import annotations

from scanning_tool.gui.tk.lifecycle import register_close_handler

__all__ = ["register_close_handler"]
