# PRD: Runtime Service Separation and Dependency Composition

## Purpose
Define the runtime architecture for the scanning tool so services, state, and presentation consumers are wired explicitly rather than depending on broad module-level globals.

## Problem Statement
The application currently relies on `scanning_tool.state.manager` imports inside many service, GUI, web, and integration modules. This creates hidden runtime dependencies, tight coupling between modules, and makes it difficult to reason about which component owns configuration, scan state, and service lifecycle.

## Goals
- Keep runtime state and configuration explicit at service boundaries.
- Limit global state access to composition/entrypoint modules only.
- Move state ownership to injected application context objects instead of module-level imports.
- Make web, GUI, and capture services consumers of injected state and service interfaces.

## Scope
### In scope
- Defining a stable application composition layer for `AppState`, config, scan state, and service state.
- Refactoring `main.py`, `WebService`, `AlignmentPoller`, `CaptureService`, and other service entrypoints to accept injected dependencies.
- Removing direct imports from `scanning_tool.state.manager` in most modules.
- Creating small, focused service interfaces or protocol abstractions where appropriate.
- Preserving existing scanner behavior while changing only wiring and state ownership.

### Out of scope
- Changing core OCR, anchor matching, or deposit lookup logic.
- Adding new scanner features.
- Rewriting the GUI frameworks or the Flask overlay technology.

## Success Criteria
- No domain or service module outside the composition layer imports `scanning_tool.state.manager` directly.
- `WebService` and GUI components consume state through constructor arguments, not globals.
- The capture pipeline and alignment polling use explicit `ConfigData`, `ScanState`, and `ServiceState` dependencies passed from the entrypoint.
- Service lifecycle methods (`start`, `stop`) are composed by a dedicated bootstrapper, not by modules that also access global state.
- Existing tests continue to pass after the state separation refactor.

## Quality Requirements
- Use constructor injection for runtime dependencies rather than module-level singletons.
- Keep `AppState` as the composition root and avoid making it a general-purpose service locator.
- Prefer narrow interfaces over broad runtime state objects when wiring behavior across package boundaries.
- Document the separation boundary in architecture docs and update any package diagrams accordingly.
