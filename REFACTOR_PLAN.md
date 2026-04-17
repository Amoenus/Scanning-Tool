# Scanning Tool Folder Structure Refactor Plan

## Objective
- Overhaul `src/scanning_tool/` from an ad-hoc mix of root modules and packages into a coherent package hierarchy.
- Preserve current behavior and entrypoints while improving maintainability, testability, and import clarity.
- Align the repository with the existing architecture guidance in `ARCHITECTURE.md`.

## Target package layout
- `src/scanning_tool/`
  - `__main__.py`
  - `main.py`
  - `config/`
  - `domain/`
  - `deposits/`
  - `services/`
  - `state/`
  - `core/`
  - `gui/`
  - `ollama/`
  - `interfaces/`
  - `logging_setup.py`
  - `web.py`
  - `runtime/` (compatibility shim only, if needed)

## Phase 1: Audit and target design
- Inventory current `src/scanning_tool` files and package relationships.
- Decide ownership for:
  - `ocr.py`
  - `hotkeys.py`
  - `web.py`
  - `runtime/`
  - `logging_setup.py`
- Document a migration map that keeps current imports working during the transition.

### Current audit summary
- `config/`, `domain/`, `deposits/`, `services/`, `state/`, `core/`, `gui/`, `ollama/`, `interfaces/`, and `runtime/` are already package-structured and aligned with the target layout.
- Root-level modules that should be preserved as bootstrap/shim entrypoints: `main.py`, `__main__.py`, `web.py`, `logging_setup.py`, `__init__.py`.
- Root-level modules that are good candidates for service ownership:
  - `ocr.py` -> `services/ocr_service.py`
  - `hotkeys.py` -> `services/hotkeys_service.py`
- `core/state_manager.py` is a central runtime state registry; keep it under `core/` for now, but evaluate whether a future `state/` wrapper should own orchestration.
- `runtime/__init__.py` is a compatibility shim and can remain as-is during migration.

### Recommended migration map
- Keep in place:
  - `src/scanning_tool/__main__.py`
  - `src/scanning_tool/main.py`
  - `src/scanning_tool/web.py`
  - `src/scanning_tool/logging_setup.py`
  - `src/scanning_tool/config/`
  - `src/scanning_tool/domain/`
  - `src/scanning_tool/deposits/`
  - `src/scanning_tool/ollama/`
  - `src/scanning_tool/core/`
  - `src/scanning_tool/state/`
  - `src/scanning_tool/gui/`
  - `src/scanning_tool/interfaces/`
  - `src/scanning_tool/runtime/`
- Move or rename for clarity in Phase 3:
  - `src/scanning_tool/ocr.py` -> `src/scanning_tool/services/ocr_service.py`
  - `src/scanning_tool/hotkeys.py` -> `src/scanning_tool/services/hotkeys_service.py`

## Phase 2: Package scaffolding and compatibility
- Create missing package `__init__.py` files for every intended package.
- Add compatibility import shims for moved modules only as short-lived migration bridges while existing imports remain in flight.
- Keep the package structure explicit and import-safe.

## Phase 3: Incremental module migration
- Move files into their target packages in small, verifiable steps.
- Update internal imports and tests after each move.
- Prefer package-based names like `services/hotkeys.py`, `services/web_service.py`, or `core/ocr.py` depending on ownership.

## Phase 4: Cleanup and stabilization
- Remove stale root-level modules after verification.
- Consolidate entrypoint wiring in `main.py` and `__main__.py`.
- Confirm the `scanning-tool` script and local install still work.
- Keep `runtime/` as a compatibility layer only if required.

## Phase 5: Validation and final review
- Run `pytest` across the repository.
- Run `mypy` and `ruff` on `src/`.
- Confirm top-level package boundaries and imports are stable.
- Review package metadata in `pyproject.toml` to ensure the installed package is correct.

## Progress
- [x] Phase 1: Audit current source package boundaries
- [x] Phase 2: Create explicit package scaffolding and shims
- [ ] Phase 3: Migrate modules into targeted packages
- [ ] Phase 4: Remove legacy root modules and finalize structure
- [ ] Phase 5: Validate runtime, tests, and static analysis

## Notes
- The current architecture guidance already recommends this package structure; this refactor will align the codebase with that guidance.
- Use compatibility shims sparingly in this single-user refactor; prefer direct imports and explicit module ownership where possible.
- A safe migration path is critical: perform one package move at a time and keep compatibility imports only until new paths are stable.
- This is a structural refactor only; business logic should remain unchanged.
