# Decision 3: Avoid backward-compatible import path shims during refactoring

**Why:** This is a single-user application untangling a monolithic script; compatibility shims prolong the mess and delay adoption of the new package layout.

**What changed:** No `runtime/__init__.py` compatibility shim was introduced. Consumers should migrate from `scanning_tool.runtime.ServiceState` to `scanning_tool.state.ServiceState`.

**Result:** Refactor clarity is preserved and the new state package can be adopted directly without adding transient alias layers.
