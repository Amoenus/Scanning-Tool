"""GUI widgets package wrapper for backwards compatibility."""

from __future__ import annotations

from scanning_tool.gui.tk.widgets import (
    ScrollableFrame,
    create_button_row,
    create_glass_scale,
    create_labeled_combobox,
    create_labeled_entry,
    create_labeled_spinbox,
    create_section_row,
    create_status_label,
)

__all__ = [
    "ScrollableFrame",
    "create_button_row",
    "create_glass_scale",
    "create_labeled_combobox",
    "create_labeled_entry",
    "create_labeled_spinbox",
    "create_section_row",
    "create_status_label",
]
