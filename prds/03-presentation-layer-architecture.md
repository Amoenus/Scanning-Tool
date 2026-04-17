# PRD: Presentation Layer Architecture

## Purpose

Define the architecture for the tool's three presentation surfaces and establish a clean separation between control, native display, and browser display.

## Problem Statement

The scanning tool currently mixes multiple UI paradigms in a way that makes it hard to reason about which components own user input versus which ones own live scan state. The native overlay and browser overlay share the same ore information, but they are not explicitly treated as renderers over the same domain source.

## Goals

- Separate the presentation layer by purpose: configuration/admin, native overlay, and browser overlay.
- Keep shared ore scan state in one domain-driven source of truth.
- Treat `gui/` and `web/` as renderers/adapters instead of independent data pipelines.
- Reduce runtime coupling by injecting state and config into the web overlay service.
- Preserve existing behavior while making the architecture easier to extend.

## Scope

### In scope

- Documenting the presentation layer responsibilities and ownership boundaries.
- Defining the data flow between config, domain state, capture services, and renderers.
- Starting the first refactor by decoupling web app creation from module-level global state.

### Out of scope

- Changing the underlying scanning or OCR behavior.
- Rewriting the native Tk UI or overlay rendering system.
- Adding remote synchronization or multi-user overlay support.

## Presentation layer responsibilities

- `gui/`
  - Control plane: configuration, scan controls, alignment tuning, and user-facing status.
  - Native overlay rendering: capture region, anchor boxes, and in-game deposit info.
- `web/`
  - Browser overlay display: a REST-backed UI that visualizes the same `ScanResult` and `DepositInfo` payloads.
- `state/` and `domain/`
  - Shared model layer: `ScanResult`, `DepositInfo`, and runtime state are the canonical source of truth.
  - `services/` produce structured domain updates that both renderers consume.

## Data flow

1. Config UI updates `config` and runtime control state.
2. Capture services update `scan_state.last_result` and alignment state.
3. Native overlay reads scan state and renders within the game overlay.
4. Web overlay reads the same `scan_state` and returns the same resolved ore details.

## Success criteria

- The browser overlay and native overlay use the same scan/domain data without duplicate parsing logic.
- The web overlay service is explicitly wired with injected state and config.
- The `gui/` package remains focused on control and native overlay rendering.
- Future renderers can be added as additional consumers of `state/` without duplicating scan logic.

## Initial implementation plan

- Introduce `WebService` in `src/scanning_tool/web/app.py` to encapsulate web overlay state and route creation.
- Update `src/scanning_tool/main.py` to instantiate the web service explicitly with `config`, `scan_state`, and `service_state`.
- Add documentation and tests to validate the new service-oriented web overlay boundary.
