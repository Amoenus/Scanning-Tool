# Architecture Decision Log

## Decision 1: Separate configuration models from domain models
**Why:** The domain layer should represent business concepts, not application settings.
**What changed:** Configuration DTOs were moved from `domain/models.py` into `config/models.py`.
**Result:** `domain` now contains only deposit, scan signature, capture, and overlay models.

## Decision 2: Consolidate runtime state into `state/`
**Why:** The repository contained both `runtime/service_state.py` and `core/state_manager.py`, which created ambiguity about where runtime state lives.
**What changed:** `service_state.py` was moved into `state/` and `state/__init__.py` was added to export state models.
**Result:** The state package now clearly owns runtime state containers, while `core/state_manager.py` remains the application registry.

## Decision 3: Keep backward-compatible import paths during refactoring
**Why:** Existing code paths and tests may still rely on `scanning_tool.runtime.ServiceState`.
**What changed:** Added `runtime/__init__.py` as a compatibility shim that re-exports `ServiceState` from `state/service_state.py`.
**Result:** Consumers can migrate at their own pace while new architecture paths are adopted.

## Decision 4: Document package boundaries and future refactor steps
**Why:** Architecture work is only effective if it is captured and shared.
**What changed:** Added `ARCHITECTURE.md`, `prds/`, and `architecture/` folders with detailed documents.
**Result:** There is now a documented plan for architecture, product goals, and decision rationale.

## Decision 5: Preserve business behavior while improving structure
**Why:** The tool must continue working as before; refactoring should not introduce feature drift.
**What changed:** The refactor focused on code organization instead of business logic.
**Result:** Validation was performed through config tests, type checking, and syntax checking for the updated files.

## Decision 6: Prefer explicit application context over broad global state
**Why:** The pipeline is simple and naturally separates into configuration and capture modes, so broad module-level runtime state is unnecessary and harder to maintain.
**What changed:** The architecture documentation now recommends moving away from the existing `core/state_manager.py` service locator toward explicit dependency injection and an application context for config/capture state.
**Result:** Future refactors will target a cleaner runtime model where configuration is loaded once and capture behavior is managed by localized pipeline objects.

## Future decisions to capture
- Split `domain/models.py` into smaller domain modules such as `ore.py`, `scan_signature.py`, `capture.py`, and `overlay.py`.
- Evaluate moving the web overlay into a dedicated `web_service.py` module.
- Add a dedicated `services/state_service.py` or similar for explicit service lifecycle management.
- Define a clear boundary between GUI state and service runtime state to reduce coupling.
