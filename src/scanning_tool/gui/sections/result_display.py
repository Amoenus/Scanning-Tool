"""Result Display section — offset sliders for the on-screen info overlay via AppContext overlay settings."""

from tkinter import ttk

from scanning_tool.gui.sections.base import SectionContext
from scanning_tool.gui.widgets import create_glass_scale
from scanning_tool.gui.overlays import (
    register_overlay_sliders,
    reposition_info_overlay,
    sync_overlay_sliders,
)


class ResultDisplaySection:
    """Display offset X/Y sliders bound to ``app_state.info_overlay_offset``."""

    def build(self, parent: ttk.Widget, ctx: SectionContext) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text="Result Display", style="Glass.TLabelframe")
        frame.pack(fill="x", padx=5, pady=8)

        self._ctx = ctx
        self._status = ctx.status

        overlay_offset = ctx.config.overlay_config.info_offset

        self._offset_x = self._make_offset_scale(
            frame, "Display offset X", -800, 800, overlay_offset.x
        )
        self._offset_y = self._make_offset_scale(
            frame, "Display offset Y", -600, 600, overlay_offset.y, padding=(0, 0)
        )

        register_overlay_sliders(self._offset_x, self._offset_y)
        sync_overlay_sliders()
        return frame

    def _make_offset_scale(
        self,
        parent: ttk.Widget,
        text: str,
        minimum: float,
        maximum: float,
        initial: float,
        padding: tuple[int, int] = (0, 4),
    ) -> ttk.Scale:
        return create_glass_scale(
            parent,
            text=text,
            minimum=minimum,
            maximum=maximum,
            initial=initial,
            command=self._on_change,
            padding=padding,
        )

    def _on_change(self, *_args: object) -> None:
        if self._ctx.control_state.syncing.overlay:
            return
        overlay_offset = self._ctx.config.overlay_config.info_offset
        overlay_offset.x = int(self._offset_x.get())
        overlay_offset.y = int(self._offset_y.get())
        self._status.set_status(
            f"Display offset updated: x={overlay_offset.x}, y={overlay_offset.y}"
        )
        reposition_info_overlay()
