# Decision 7: Preserve shared GUI state and keep overlay API Tk-agnostic

**Why:**
The GUI duplication refactor must reduce repeated state and overlay logic while preserving a clean package boundary for future non-Tk backends like PyQt6.

**What changed:**
- Centralized shared GUI state models in `src/scanning_tool/gui/state.py`.
- Simplified `src/scanning_tool/gui/tk/control_state.py` to reuse the shared `ControlState`.
- Consolidated overlay state handling behind `src/scanning_tool/gui/overlay_state.py` and removed redundant Tk-specific overlay state definitions.
- Updated `src/scanning_tool/gui/overlays/__init__.py` to avoid importing Tk-specific overlay modules at import time and to lazily delegate to `scanning_tool.gui.tk.overlays` only when overlay functions are called.
- Re-exported shared layout types in `src/scanning_tool/gui/tk/layout.py` from the generic `src/scanning_tool/gui/layout.py`.
- Added regression coverage for `scanning_tool.gui.overlays` import boundaries and overlay wrapper exports.
- Verified the refactor with `duplicate_scan.py`, confirming the original GUI overlay wrapper duplication is gone.

**Result:**
The GUI refactor now has a clearer boundary between shared backend-agnostic model code and the Tk adapter. The generic overlay API remains import-safe for future non-Tk backends, and the duplicated overlay wrapper code has been eliminated.
