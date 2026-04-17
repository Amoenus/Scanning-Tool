# PRD: Technical Architecture

## Purpose
This document explains the current and target architecture for the scanning tool, with a focus on package separation, runtime flow, and the refactor plan discussed during the recent design pass.

## Architecture overview
The application is organized into distinct layers:

- `config/`: configuration loading and typed settings models.
- `domain/`: business-domain types, data transfer objects, and parsing helpers.
- `deposits/`: deposit metadata, ore tables, scan signature loading, and lookup logic.
- `services/`: background services for capture, alignment, Ollama integration, and config management.
- `state/`: runtime state containers for scanning, service state, overlays, and control state.
- `core/anchor/`: low-level anchor template matching and tracker implementation.
- `gui/`: GUI sections, overlay rendering, and app lifecycle.
- `ollama/`: wrapper modules for host install, client interaction, and model management.
- `web.py`: Flask app exposing the overlay.

## Key design principles
- **Single responsibility**: each package owns a focused concern.
- **Strong typing**: domain models and config models use explicit dataclasses and Pydantic when needed.
- **Minimal runtime coupling**: avoid broad global mutable state; prefer explicit application context and constructor injection for the capture pipeline.
- **Backward-compatible refactoring**: `runtime/__init__.py` is retained temporarily as a compatibility shim while new import paths are stabilized; avoid shims as enduring architecture in this single-user refactor.

## Operation model
The scanner is best understood as two modes:

- **Configuration mode**: select the OCR model, set anchor search bounds, and define the OCR capture region.
- **Capture mode**: fire the scan pipeline with hotkeys and produce decoded deposit data.

Configuration state is largely static once the session starts, while capture state should be localized to the live scanning pipeline.

## Runtime flow
1. Start the application via `scanning-tool` entrypoint or `main.py`.
2. `main.py` loads config, initializes services, creates anchor tracking, starts hotkey and web threads, then launches the GUI.
3. Capture service reads the configured screen region and passes image data to the OCR pipeline.
4. Anchor alignment uses templates to adjust capture region and maintain stability.
5. OCR results are mapped to structured `ScanResult` and `DepositInfo` domain objects.
6. GUI and web overlay render the latest scan results.

## Current refactor plan
- Keep the current business behavior unchanged while improving architecture.
- Move configuration DTOs into a dedicated `config/` package.
- Consolidate runtime state into `state/` and add clear package exports.
- Continue splitting large domain model files into focused modules where appropriate.
- Consider moving `web.py` into a service module for consistency, with the Flask app instantiated by a dedicated web service.

## What this enables
- Easier maintenance and future extensions.
- Clearer onboarding for new contributors.
- Reduced risk when adding new services like remote Ollama hosts, multi-overlay support, or improved OCR flows.
- Better testability by decoupling configuration, runtime state, and capture logic.
- A clearer migration path away from broad global state toward explicit application context.
