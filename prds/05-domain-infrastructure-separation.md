# PRD: Domain and Infrastructure Boundary Separation

## Purpose
Establish a clean boundary between pure domain models, configuration data, runtime state, and external infrastructure integrations in the scanning tool.

## Problem Statement
The current codebase mixes domain responsibilities, configuration handling, and infrastructure concerns. Examples include:
- `service_state` containing both Ollama process state and rock deposit caches.
- `ollama.host` and `ollama.client` modules reading global config and environment state directly.
- `deposits.lookup` depending on a global `service_state` cache instead of an explicit repository or lookup service.
- The Flask `WebService` combining template rendering, state access, and deposit table selection in one module.

This weakens conceptual separation and makes the system harder to test, extend, and reason about.

## Goals
- Keep domain models and business types isolated from runtime state and infrastructure concerns.
- Separate configuration models from service runtime state and from external integration adapters.
- Treat `deposits`, `ollama`, `capture`, and `web` as infrastructure adapters that depend on explicit domain and config inputs.
- Use explicit bootstrap wiring for adapters and handler registration, rather than scattering runtime composition through domain or state modules.
- Simplify `service_state` so it owns only runtime metadata and adapter state, not unrelated domain caches.

## Scope
### In scope
- Defining explicit boundaries for domain models (`scanning_tool.domain`), configuration (`scanning_tool.config`), and runtime caches/services (`scanning_tool.state`).
- Refactoring the Ollama integration to separate host normalization and client creation from global state access.
- Refactoring deposit lookup logic to accept explicit `RockData`/`DepositTable` repositories instead of importing `service_state`.
- Encapsulating external adapters like Flask and screen capture behind small, injectable service abstractions.
- Ensuring the browser overlay only consumes rendered scan results and config data, not broad global state.

### Out of scope
- Replacing the underlying OCR provider or its capabilities.
- Altering the domain shape of `ScanResult`, `DepositInfo`, or other business models.
- Adding support for remote or multi-user services.

## Success Criteria
- `ollama.host` and `ollama.client` no longer import `scanning_tool.state.manager` from inside adapter code.
- `deposits.lookup` consumes explicit repository interfaces and is independent of a global cache.
- `service_state` is scoped to runtime adapter metadata, not a catch-all for unrelated state.
- Infrastructure adapters expose clear, isolated interfaces that can be mocked or replaced in tests.
- Adapter wiring and handler registration happen in bootstrap/entrypoint code rather than via hidden global imports in domain or runtime modules.
- The existing Flask API and GUI rendering behavior remain unchanged.

## Quality Requirements
- Use strongly typed dataclasses or typed models for configuration, domain, and service state.
- Avoid mixed-purpose objects and keep package responsibilities narrow.
- Prefer composition of pure domain services with infrastructure adapters, rather than embedding infrastructure details inside core business logic.
- Document the domain/infrastructure boundaries in `architecture/README.md` and link to this PRD from the existing architecture docs.
