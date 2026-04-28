# PRD: Bootstrap Event Wiring for Internal Signals

## Purpose
Centralize event listener registration in bootstrap/entrypoint code instead of scattering wiring throughout UI modules and service internals.

## Problem Statement
Event listeners and signal subscriptions are currently registered in multiple places such as `gui/tk/app.py`, `web/app.py`, and state classes. This makes the event architecture harder to understand, harder to modify, and less predictable.

## Goals
- Keep event handler registration in a few dedicated bootstrap modules.
- Prevent UI modules from becoming responsible for composing internal event flows.
- Enable easier testing of event wiring by isolating it from business logic.

## Scope
### In scope
- Identify the current event wiring locations in Tk GUI, web app, and any entrypoint modules.
- Create one or more bootstrap/assembler modules responsible for connecting domain/service events to UI/web adapters.
- Refactor UI modules to expose handler registration endpoints rather than connecting directly to signals themselves.
- Document the bootstrap wiring pattern in architecture docs.

### Out of scope
- Rewriting the entire GUI architecture.
- Changing the underlying event library.

## Success Criteria
- UI modules like `gui/tk/app.py` and `web/app.py` no longer perform their own global event registration directly.
- A dedicated bootstrap module manages signal/router wiring consistently.
- Event subscriptions are easier to inspect and reason about from a single composition point.
- Tests verify the bootstrap wiring behavior and ensure the same event flow remains intact.

## Quality Requirements
- Keep bootstrap modules simple and descriptive.
- Do not place business logic inside wiring code.
- Use explicit adapter interfaces to connect events to UI consumers.
- Make the wiring pattern easy to document and maintain.

## Implementation Checklist
- [ ] Inventory current event listener registration sites.
- [ ] Add a bootstrap module to wire service/state events to UI and web handlers.
- [ ] Refactor UI modules to accept adapter hooks or explicit listener registration.
- [ ] Document the new wiring approach in architecture docs.
- [ ] Add tests covering the bootstrap wiring.
