# Decision 2: Consolidate runtime state into `state/`

**Why:** The repository contained both `runtime/service_state.py` and `core/state_manager.py`, which created ambiguity about where runtime state lives.

**What changed:** `service_state.py` was moved into `state/` and `state/__init__.py` was added to export state models.

**Result:** The state package now clearly owns runtime state containers, while `core/state_manager.py` remains the application registry.
