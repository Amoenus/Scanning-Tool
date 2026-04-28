# PRD: Event Bus Abstraction for Internal Signals

## Purpose
Introduce an explicit event bus abstraction so internal event dispatch can be wired, tested, and replaced without leaking the `blinker` API across business logic.

## Problem Statement
Multiple modules currently import shared `blinker.Signal` objects directly from `state.signals` and call `send(...)` in business code. This tightly couples services and use cases to the concrete signaling mechanism and makes it harder to test or change event delivery semantics.

## Goals
- Define a lightweight event bus or emitter interface for internal application events.
- Use constructor injection to provide the event bus to services and application workflows.
- Keep `blinker` as the default implementation while hiding it behind an interface.
- Preserve existing event flow for UI and web subscribers.

## Scope
### In scope
- Create an `EventBus` abstraction in a shared `state` or `core` package.
- Implement a `BlinkerEventBus` default adapter using existing `state.signals`.
- Refactor `CaptureUseCase`, `AlignmentService`, and other event-emitting modules to depend on the interface.
- Update tests to mock or stub the event bus rather than requiring real signal objects.

### Out of scope
- Replacing `blinker` with a different library.
- Changing external event-driven features such as Flask SSE semantics.
- Rewriting all existing listeners immediately.

## Success Criteria
- Services no longer import `state.signals` directly for dispatching events.
- Business code accepts an `EventBus` or `EventDispatcher` dependency.
- The application still emits status and state-change notifications correctly.
- Tests can assert event emission through a mocked event bus.

## Quality Requirements
- Keep the event bus interface minimal and focused on application-level signals.
- Avoid exposing `blinker.Signal` types in public service APIs.
- Maintain strong typing for event names and payloads.
- Use dependency injection rather than module-level event globals.

## Implementation Checklist
- [ ] Define `EventBus`/`EventDispatcher` abstraction in `src/scanning_tool/state`.
- [ ] Implement a default `BlinkerEventBus` adapter using `state.signals`.
- [ ] Refactor event-producing services to receive the event bus through constructors.
- [ ] Update event consumption wiring to remain compatible with the adapter.
- [ ] Add tests for the event bus abstraction and service wiring.
