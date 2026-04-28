# Decision: Use blinker for in-process event signaling

## Status
Accepted

## Context
The Scanning Tool already uses `blinker` for application state and UI signaling in a few modules.

We need a consistent mechanism for internal event dispatch and signal handling across the runtime, GUI, and service components.

## Decision
Use `blinker` as the repo’s standard internal event bus library for in-process message dispatch and signal wiring.

## Consequences
- We avoid designing a custom message bus from scratch for in-process dispatch.
- Internal event handling remains lightweight and explicit.
- We can reuse an established library already declared in `pyproject.toml`.
- External event broker libraries are not needed unless the architecture later evolves to cross-process or distributed messaging.
