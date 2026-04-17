# Scanning Tool Architecture Guide

## Goals
- Separate domain models from configuration models.
- Consolidate application state into a single `state` package.
- Preserve existing runtime compatibility while making package boundaries explicit.
- Keep business logic unchanged; only improve module organization.

## Recommended package layout

- `scanning_tool/`
  - `__main__.py`
  - `main.py` — application bootstrap and startup orchestration.
  - `config/`
    - `loader.py` — resource paths and file resolution.
    - `models.py` — configuration DTOs for app settings.
    - `__init__.py`
  - `domain/`
    - `models.py` — core business data types: deposits, scan signatures, results, capture region, alignment.
    - `dtos.py` — raw external data shapes.
  - `deposits/`
    - `lookup.py`
    - `tables.py`
    - `scan_signatures.py`
    - `ore_tiers.py`
  - `services/`
    - `base_service.py`
    - `capture_service.py`
    - `alignment_service.py`
    - `ollama_service.py`
    - `config_service.py`
  - `state/`
    - `scan_state.py`
    - `service_state.py`
    - `__init__.py`
  - `core/`
    - `anchor/` — low level anchor-tracking implementation and helpers.
    - `state_manager.py` — centralized runtime state registry.
  - `gui/`
    - application UI components and overlay state.
  - `ollama/`
    - Ollama host, client, and installer support.
  - `web.py` — Flask web server application.

## What changed
- Moved configuration-specific models into `src/scanning_tool/config/models.py`.
- Updated `src/scanning_tool/services/config_service.py` to import config DTOs from `scanning_tool.config.models`.
- Consolidated runtime service state into `src/scanning_tool/state/service_state.py`.
- Added `src/scanning_tool/state/__init__.py` to expose state model exports.
- Added `src/scanning_tool/runtime/__init__.py` as a compatibility shim for existing import paths.
- Removed config model definitions from `src/scanning_tool/domain/models.py`.

## Why this helps
- `domain` now represents business concepts, not configuration shapes.
- `config` is now a dedicated package for loading and persisting settings.
- `state` is a coherent package for runtime state objects, reducing the need for an ambiguous `runtime` package.
- Clear package boundaries make future refactors safer and minimize import friction.
- Configuration state is isolated from capture state, making the live scan pipeline easier to reason about.
- The current global state usage is now identified as a refactor debt; the preferred architecture moves toward an explicit application context and parameterized capture pipeline.

## Preferred runtime model
- Load configuration once at startup and treat it as mostly static.
- Build a capture pipeline object with injected dependencies and explicit runtime state.
- Keep capture, alignment, and overlay behavior local to the owning service or pipeline.
- Reserve global state only for compatibility shims and bootstrap wiring.

## Next steps
- Consider splitting `domain/models.py` further into smaller domain modules (`ore.py`, `scan_signature.py`, `capture.py`, `overlay.py`).
- Evaluate whether `web.py` should be moved into `services/web_service.py` for consistency.
- Add package-level `__init__.py` files for `state` and `runtime` to make the package structure explicit.
