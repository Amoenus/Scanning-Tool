# Decision 6: Prefer explicit application context over broad global state

**Why:** The pipeline is simple and naturally separates into configuration and capture modes, so broad module-level runtime state is unnecessary and harder to maintain.

**What changed:** The architecture documentation now recommends moving away from the existing `core/state_manager.py` service locator toward explicit dependency injection and an application context for config/capture state.

**Result:** Future refactors will target a cleaner runtime model where configuration is loaded once and capture behavior is managed by localized pipeline objects.
