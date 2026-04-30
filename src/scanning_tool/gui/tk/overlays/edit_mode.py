"""Edit mode support for the Tk overlay implementation."""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from scanning_tool.gui.actions import publish_ui_action
from scanning_tool.gui.edit_mode import EditModeRenderer
from scanning_tool.state.actions.edit_mode import EditModeAction
from scanning_tool.state.read_models.edit_mode import ActiveRegion, EditModeReadModel
from scanning_tool.state.signals.edit_mode import edit_mode_changed
from scanning_tool.gui.tk.overlays.anchor import (
    preview_anchor_region,
    reset_anchor_region,
)
from scanning_tool.gui.tk.overlays.capture import (
    preview_capture_region,
    reset_capture_region,
)
from scanning_tool.gui.tk.overlays.info import preview_info_overlay_position, reposition_info_overlay
from scanning_tool.gui.tk.overlays.slider_sync import (
    sync_anchor_sliders,
    sync_capture_sliders,
    sync_overlay_sliders,
)
from scanning_tool.gui.tk.overlays.base import (
    ANCHOR_OVERLAY_PAD,
    CAPTURE_OVERLAY_PADDING_X,
    CAPTURE_OVERLAY_PADDING_Y,
    safe_tk,
)
from scanning_tool.gui.state import OverlayState, ControlState
from scanning_tool.domain.alignment import CaptureRegion

if TYPE_CHECKING:
    from scanning_tool.config.models import OverlayConfig

HANDLE_RADIUS = 12
HANDLE_FILL = "#ffff00"
ACTIVE_BORDER_COLOR = "#f5b041"
INACTIVE_CAPTURE_COLOR = "red"
INACTIVE_ANCHOR_COLOR = "#00d4ff"


@dataclass
class _DragSession:
    region: ActiveRegion
    action: str
    handle: str
    start_x: int
    start_y: int
    original_values: dict[str, int]


class _EditModeToolbar:
    def __init__(self) -> None:
        self.root: tk.Toplevel | None = None
        self.region_label: tk.Label | None = None
        self.dim_label: tk.Label | None = None
        self.hint_label: tk.Label | None = None

    def show(self) -> None:
        if self.root and tk.Toplevel.winfo_exists(self.root):
            return

        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#222222")

        frame = tk.Frame(self.root, bg="#222222", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        self.region_label = tk.Label(
            frame,
            text="Edit Mode",
            fg="white",
            bg="#222222",
            font=("Arial", 10, "bold"),
        )
        self.region_label.pack(anchor="w", padx=8, pady=(8, 2))

        self.dim_label = tk.Label(
            frame,
            text="",
            fg="white",
            bg="#222222",
            font=("Arial", 10),
        )
        self.dim_label.pack(anchor="w", padx=8)

        button_frame = tk.Frame(frame, bg="#222222")
        button_frame.pack(anchor="w", pady=8, padx=8)

        tk.Button(
            button_frame,
            text="Exit",
            command=lambda: publish_ui_action(EditModeAction.EXIT_EDIT_MODE),
            width=6,
        ).pack(side="left", padx=(0, 4))
        tk.Button(
            button_frame,
            text="Reset",
            command=lambda: publish_ui_action(EditModeAction.RESET_REGION),
            width=6,
        ).pack(side="left", padx=(0, 4))
        tk.Button(
            button_frame,
            text="Lock",
            state="disabled",
            width=6,
        ).pack(side="left")

        self.hint_label = tk.Label(
            frame,
            text="Tab: cycle • Arrows: nudge • Esc: exit",
            fg="#cccccc",
            bg="#222222",
            font=("Arial", 8),
        )
        self.hint_label.pack(anchor="w", padx=8, pady=(0, 8))

    def hide(self) -> None:
        if self.root and tk.Toplevel.winfo_exists(self.root):
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        self.root = None
        self.region_label = None
        self.dim_label = None
        self.hint_label = None

    def update(self, active_region: ActiveRegion | None, dims: str) -> None:
        if self.root is None or not tk.Toplevel.winfo_exists(self.root):
            return
        if self.region_label is not None:
            self.region_label.config(text=f"{active_region.value.title()} region" if active_region else "Edit Mode")
        if self.dim_label is not None:
            self.dim_label.config(text=dims)

    def position_near(self, target_root: tk.Toplevel | None) -> None:
        if self.root is None or target_root is None:
            return
        self.root.update_idletasks()
        try:
            target_x = target_root.winfo_rootx()
            target_y = target_root.winfo_rooty()
            target_w = target_root.winfo_width()
            toolbar_w = self.root.winfo_width()
            toolbar_h = self.root.winfo_height()
            left = max(0, target_x + target_w - toolbar_w)
            top = max(0, target_y - toolbar_h - 10)
            self.root.geometry(f"{toolbar_w}x{toolbar_h}+{left}+{top}")
        except tk.TclError:
            pass


class EditModeOverlayManager(EditModeRenderer):
    def __init__(
        self,
        overlay_state: OverlayState,
        control_state: ControlState,
        config,
    ) -> None:
        self._overlay_state = overlay_state
        self._control_state = control_state
        self._config = config
        self._state = EditModeReadModel()
        self._edit_mode = False
        self._drag_session: _DragSession | None = None
        self._toolbar = _EditModeToolbar()
        self._screen_blocker_root: tk.Toplevel | None = None
        self._bound_canvases: set[int] = set()
        self._bound_roots: set[int] = set()

    def install(self) -> None:
        self._bind_root_listeners()
        self._bind_existing_overlay_roots()
        edit_mode_changed.connect(self._on_edit_mode_changed, weak=False)

    def destroy(self) -> None:
        edit_mode_changed.disconnect(self._on_edit_mode_changed)

    def _bind_root_listeners(self) -> None:
        self._overlay_state.add_capture_overlay_root_listener(
            lambda root: self._bind_capture_overlay_root(root),
        )
        self._overlay_state.add_anchor_overlay_root_listener(
            lambda root: self._bind_anchor_overlay_root(root),
        )
        self._overlay_state.add_info_overlay_root_listener(
            lambda root: self._bind_info_overlay_root(root),
        )

    def _bind_existing_overlay_roots(self) -> None:
        self._bind_capture_overlay_root(self._overlay_state.capture_overlay_root)
        self._bind_anchor_overlay_root(self._overlay_state.anchor_overlay_root)
        self._bind_info_overlay_root(self._overlay_state.info_overlay_root)

    def _bind_capture_overlay_root(self, root: Any | None) -> None:
        canvas = self._overlay_state.capture_overlay_canvas
        if root is None or canvas is None:
            return
        if id(canvas) in self._bound_canvases:
            return
        canvas.bind("<ButtonPress-1>", lambda event: self._on_mouse_down(event, ActiveRegion.CAPTURE), add="+")
        canvas.bind("<B1-Motion>", self._on_mouse_move, add="+")
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up, add="+")
        self._bind_key_handlers(root)
        self._bound_canvases.add(id(canvas))

    def _bind_anchor_overlay_root(self, root: Any | None) -> None:
        canvas = self._overlay_state.anchor_overlay_canvas
        if root is None or canvas is None:
            return
        if id(canvas) in self._bound_canvases:
            return
        canvas.bind("<ButtonPress-1>", lambda event: self._on_mouse_down(event, ActiveRegion.ANCHOR), add="+")
        canvas.bind("<B1-Motion>", self._on_mouse_move, add="+")
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up, add="+")
        self._bind_key_handlers(root)
        self._bound_canvases.add(id(canvas))

    def _bind_info_overlay_root(self, root: Any | None) -> None:
        canvas = self._overlay_state.info_overlay_canvas
        if root is None or canvas is None:
            return
        if id(canvas) in self._bound_canvases:
            return
        canvas.bind("<ButtonPress-1>", lambda event: self._on_mouse_down(event, ActiveRegion.INFO), add="+")
        canvas.bind("<B1-Motion>", self._on_mouse_move, add="+")
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up, add="+")
        self._bind_key_handlers(root)
        self._bound_canvases.add(id(canvas))

    def _bind_key_handlers(self, root: Any) -> None:
        if id(root) in self._bound_roots:
            return
        try:
            root.bind("<Escape>", self._on_escape, add="+")
            root.bind("<Tab>", self._on_tab, add="+")
            root.bind("<Left>", self._on_arrow_left, add="+")
            root.bind("<Right>", self._on_arrow_right, add="+")
            root.bind("<Up>", self._on_arrow_up, add="+")
            root.bind("<Down>", self._on_arrow_down, add="+")
            root.bind("<Shift-Left>", self._on_shift_arrow_left, add="+")
            root.bind("<Shift-Right>", self._on_shift_arrow_right, add="+")
            root.bind("<Shift-Up>", self._on_shift_arrow_up, add="+")
            root.bind("<Shift-Down>", self._on_shift_arrow_down, add="+")
        except tk.TclError:
            pass
        self._bound_roots.add(id(root))

    def _on_mouse_down(self, event: tk.Event, region: ActiveRegion) -> None:
        if not self._edit_mode:
            return
        canvas = event.widget
        root = canvas.winfo_toplevel()
        try:
            root.focus_force()
        except tk.TclError:
            pass
        canvas.grab_set()

        effective = self._effective_region(region)
        if effective is None:
            return

        click_in_region = self._point_inside_region(event, region, effective)
        if not click_in_region:
            return

        publish_ui_action(EditModeAction.SELECT_REGION, {"region": region.value})
        handle = self._pick_handle(event, region, effective)
        self._drag_session = _DragSession(
            region=region,
            action="move" if handle == "inside" else "resize",
            handle=handle,
            start_x=event.x_root,
            start_y=event.y_root,
            original_values=self._region_values(effective),
        )

    def _on_mouse_move(self, event: tk.Event) -> None:
        if not self._edit_mode or self._drag_session is None:
            return
        session = self._drag_session
        dx = event.x_root - session.start_x
        dy = event.y_root - session.start_y
        payload: dict[str, int] = {}

        if session.region in (ActiveRegion.CAPTURE, ActiveRegion.ANCHOR):
            original = session.original_values
            left = original["left"]
            top = original["top"]
            width = original["width"]
            height = original["height"]
            if session.handle == "inside":
                payload = {"left": left + dx, "top": top + dy, "width": width, "height": height}
            else:
                payload = self._resize_payload(session.handle, left, top, width, height, dx, dy)
        else:
            original_x = session.original_values["x"]
            original_y = session.original_values["y"]
            payload = {"x": original_x + dx, "y": original_y + dy}

        publish_ui_action(EditModeAction.DRAG_REGION, payload)

    def _on_mouse_up(self, event: tk.Event) -> None:
        canvas = event.widget
        try:
            canvas.grab_release()
        except tk.TclError:
            pass
        if not self._edit_mode or self._drag_session is None:
            return
        publish_ui_action(EditModeAction.COMMIT_REGION)
        self._drag_session = None

    def _on_escape(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.EXIT_EDIT_MODE)
        return "break"

    def _on_tab(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.CYCLE_REGION)
        return "break"

    def _on_arrow_left(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": -1})
        return "break"

    def _on_arrow_right(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": 1})
        return "break"

    def _on_arrow_up(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": -1})
        return "break"

    def _on_arrow_down(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": 1})
        return "break"

    def _on_shift_arrow_left(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": -10})
        return "break"

    def _on_shift_arrow_right(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_left": 10})
        return "break"

    def _on_shift_arrow_up(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": -10})
        return "break"

    def _on_shift_arrow_down(self, event: tk.Event) -> str:
        publish_ui_action(EditModeAction.NUDGE_REGION, {"delta_top": 10})
        return "break"

    def _on_edit_mode_changed(self, sender: object, state: EditModeReadModel | None = None) -> None:
        if state is None:
            return
        self._state = state
        self._edit_mode = state.is_edit_mode
        if self._edit_mode:
            self._create_screen_blocker()
            self._set_overlay_windows_editable(True)
            self._toolbar.show()
            self._sync_sliders()
            self._update_previews()
            self._refresh_toolbar()
            self._lift_edit_mode_windows()
        else:
            self._toolbar.hide()
            self._destroy_screen_blocker()
            self._set_overlay_windows_editable(False)
            self._restore_overlays()
            self._sync_sliders()

    def _sync_sliders(self) -> None:
        if self._state.active_region == ActiveRegion.CAPTURE:
            capture_region = self._effective_capture_region()
            if capture_region is not None:
                sync_capture_sliders(self._control_state, capture_region)
            return

        if self._state.active_region == ActiveRegion.ANCHOR:
            anchor_region = self._effective_anchor_region()
            if anchor_region is not None:
                sync_anchor_sliders(
                    self._control_state,
                    anchor_region,
                    self._config.anchor_offset,
                )
            return

        if self._state.active_region == ActiveRegion.INFO:
            offset = self._effective_info_offset()
            sync_overlay_sliders(self._control_state, offset)
            return

    def _update_previews(self) -> None:
        if self._state.active_region == ActiveRegion.CAPTURE:
            capture_region = self._effective_capture_region()
            if capture_region is not None:
                preview_capture_region(capture_region)
                self._highlight_capture_overlay(active=True)
        else:
            reset_capture_region(self._config.capture_region)
            self._highlight_capture_overlay(active=False)

        if self._state.active_region == ActiveRegion.ANCHOR:
            anchor_region = self._effective_anchor_region()
            if anchor_region is not None:
                preview_anchor_region(anchor_region, self._overlay_state)
                self._highlight_anchor_overlay(active=True)
        else:
            reset_anchor_region(self._config.anchor_template, self._overlay_state)
            self._highlight_anchor_overlay(active=False)

        if self._state.active_region == ActiveRegion.INFO:
            offset = self._effective_info_offset()
            preview_info_overlay_position(
                self._overlay_state,
                self._config.overlay_config,
                offset.x,
                offset.y,
            )
        else:
            reposition_info_overlay(self._overlay_state, self._config.overlay_config)

    def _restore_overlays(self) -> None:
        reset_capture_region(self._config.capture_region)
        reset_anchor_region(self._config.anchor_template, self._overlay_state)
        reposition_info_overlay(self._overlay_state, self._config.overlay_config)
        self._highlight_capture_overlay(active=False)
        self._highlight_anchor_overlay(active=False)

    def _refresh_toolbar(self) -> None:
        active_region = self._state.active_region
        dims = ""
        if active_region == ActiveRegion.CAPTURE:
            capture_region = self._effective_capture_region()
            if capture_region is not None:
                dims = f"{capture_region.left},{capture_region.top} {capture_region.width}x{capture_region.height}"
        elif active_region == ActiveRegion.ANCHOR:
            anchor_region = self._effective_anchor_region()
            if anchor_region is not None:
                dims = f"{anchor_region.left},{anchor_region.top} {anchor_region.width}x{anchor_region.height}"
        elif active_region == ActiveRegion.INFO:
            offset = self._effective_info_offset()
            dims = f"{offset.x},{offset.y}"
        self._toolbar.update(active_region, dims)
        target_root = self._root_for_active_region()
        self._toolbar.position_near(target_root)

    def _create_screen_blocker(self) -> None:
        if self._screen_blocker_root is not None:
            return

        blocker = tk.Toplevel()
        blocker.overrideredirect(True)
        blocker.attributes("-topmost", True)
        blocker.attributes("-alpha", 0.01)
        blocker.configure(bg="black")

        screen_width = safe_tk(blocker.winfo_screenwidth, 1920) or 1920
        screen_height = safe_tk(blocker.winfo_screenheight, 1080) or 1080
        blocker.geometry(f"{screen_width}x{screen_height}+0+0")
        try:
            blocker.focus_force()
        except tk.TclError:
            pass

        blocker.bind("<ButtonPress>", lambda event: "break", add="+")
        blocker.bind("<ButtonRelease>", lambda event: "break", add="+")
        blocker.bind("<MouseWheel>", lambda event: "break", add="+")
        blocker.bind("<Button-4>", lambda event: "break", add="+")
        blocker.bind("<Button-5>", lambda event: "break", add="+")
        self._bind_key_handlers(blocker)
        self._screen_blocker_root = blocker

    def _destroy_screen_blocker(self) -> None:
        if self._screen_blocker_root and safe_tk(self._screen_blocker_root.winfo_exists, False):
            try:
                self._screen_blocker_root.destroy()
            except tk.TclError:
                pass
        self._screen_blocker_root = None

    def _set_overlay_windows_editable(self, enable: bool) -> None:
        for root in (
            self._overlay_state.capture_overlay_root,
            self._overlay_state.anchor_overlay_root,
            self._overlay_state.info_overlay_root,
        ):
            if root is None or not safe_tk(root.winfo_exists, False):
                continue
            try:
                root.attributes("-transparentcolor", "black")
            except tk.TclError:
                pass

    def _lift_edit_mode_windows(self) -> None:
        if self._screen_blocker_root and safe_tk(self._screen_blocker_root.winfo_exists, False):
            safe_tk(self._screen_blocker_root.lift)

        for root in (
            self._overlay_state.capture_overlay_root,
            self._overlay_state.anchor_overlay_root,
            self._overlay_state.info_overlay_root,
            self._toolbar.root,
        ):
            if root is not None:
                safe_tk(root.lift)

    def _highlight_capture_overlay(self, active: bool) -> None:
        canvas = self._overlay_state.capture_overlay_canvas
        rect_id = self._overlay_state.capture_rect_id
        if canvas is None or rect_id is None:
            return
        safe = canvas.itemconfig
        try:
            canvas.itemconfig(rect_id, outline=ACTIVE_BORDER_COLOR if active else INACTIVE_CAPTURE_COLOR)
        except tk.TclError:
            pass

    def _highlight_anchor_overlay(self, active: bool) -> None:
        canvas = self._overlay_state.anchor_overlay_canvas
        rect_id = self._overlay_state.anchor_rect_id
        if canvas is None or rect_id is None:
            return
        try:
            canvas.itemconfig(rect_id, outline=ACTIVE_BORDER_COLOR if active else INACTIVE_ANCHOR_COLOR)
        except tk.TclError:
            pass

    def _root_for_active_region(self) -> tk.Toplevel | None:
        if self._state.active_region == ActiveRegion.CAPTURE:
            return self._overlay_state.capture_overlay_root
        if self._state.active_region == ActiveRegion.ANCHOR:
            return self._overlay_state.anchor_overlay_root
        if self._state.active_region == ActiveRegion.INFO:
            return self._overlay_state.info_overlay_root
        return None

    def _effective_capture_region(self) -> CaptureRegion | None:
        return self._config.capture_region

    def _effective_anchor_region(self) -> CaptureRegion | None:
        return self._config.anchor_template

    def _effective_info_offset(self) -> Any:
        return self._config.overlay_config.info_offset

    def _region_values(self, region: CaptureRegion) -> dict[str, int]:
        return {
            "left": int(region.left),
            "top": int(region.top),
            "width": int(region.width),
            "height": int(region.height),
        }

    def _resize_payload(
        self,
        handle: str,
        left: int,
        top: int,
        width: int,
        height: int,
        dx: int,
        dy: int,
    ) -> dict[str, int]:
        new_left = left
        new_top = top
        new_width = width
        new_height = height
        if handle in ("nw", "w", "sw"):
            new_left = left + dx
            new_width = width - dx
        if handle in ("ne", "e", "se"):
            new_width = width + dx
        if handle in ("nw", "n", "ne"):
            new_top = top + dy
            new_height = height - dy
        if handle in ("sw", "s", "se"):
            new_height = height + dy

        return {
            "left": max(0, new_left),
            "top": max(0, new_top),
            "width": max(20, new_width),
            "height": max(20, new_height),
        }

    def _point_inside_region(
        self,
        event: tk.Event,
        region: ActiveRegion,
        effective: CaptureRegion,
    ) -> bool:
        if region == ActiveRegion.CAPTURE:
            x = event.x - CAPTURE_OVERLAY_PADDING_X // 2
            y = event.y - CAPTURE_OVERLAY_PADDING_Y
            return 0 <= x <= effective.width and 0 <= y <= effective.height
        if region == ActiveRegion.ANCHOR:
            x = event.x - ANCHOR_OVERLAY_PAD // 2
            y = event.y - ANCHOR_OVERLAY_PAD // 2
            return 0 <= x <= effective.width and 0 <= y <= effective.height
        return True

    def _pick_handle(
        self,
        event: tk.Event,
        region: ActiveRegion,
        effective: CaptureRegion,
    ) -> str:
        if region == ActiveRegion.INFO:
            return "inside"

        if region == ActiveRegion.CAPTURE:
            offset_x = CAPTURE_OVERLAY_PADDING_X // 2
            offset_y = CAPTURE_OVERLAY_PADDING_Y
        else:
            offset_x = ANCHOR_OVERLAY_PAD // 2
            offset_y = ANCHOR_OVERLAY_PAD // 2

        x = event.x - offset_x
        y = event.y - offset_y
        width = effective.width
        height = effective.height
        r = HANDLE_RADIUS

        near_left = x <= r
        near_right = x >= width - r
        near_top = y <= r
        near_bottom = y >= height - r

        if near_left and near_top:
            return "nw"
        if near_right and near_top:
            return "ne"
        if near_left and near_bottom:
            return "sw"
        if near_right and near_bottom:
            return "se"
        if near_left:
            return "w"
        if near_right:
            return "e"
        if near_top:
            return "n"
        if near_bottom:
            return "s"
        return "inside"


def install_edit_mode_overlay(
    overlay_state: OverlayState,
    control_state: ControlState,
    config,
) -> EditModeOverlayManager:
    manager = EditModeOverlayManager(overlay_state, control_state, config)
    manager.install()
    return manager
