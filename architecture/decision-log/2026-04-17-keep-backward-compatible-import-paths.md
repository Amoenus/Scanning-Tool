# Decision 3: Keep backward-compatible import paths during refactoring

**Why:** Existing code paths and tests may still rely on `scanning_tool.runtime.ServiceState`.

**What changed:** Added `runtime/__init__.py` as a compatibility shim that re-exports `ServiceState` from `state/service_state.py`.

**Result:** Consumers can migrate at their own pace while new architecture paths are adopted.
