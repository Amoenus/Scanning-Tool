# PRD: Typed Event Payloads for Internal Signals

## Purpose
Make internal event payloads explicit and strongly typed so listeners can depend on a clear contract rather than ad hoc keyword arguments.

## Problem Statement
Current signal handlers consume generic kwargs such as `message=...`, `scan_result=...`, or `alignment_info=...`. This creates weak contracts, reduces discoverability, and makes event consumers brittle when payload structure changes.

## Goals
- Define small immutable event payload data classes for major internal events.
- Use those payload objects consistently in signal emitters and listeners.
- Keep event contracts easy to document and inspect.

## Scope
### In scope
- Create typed event payloads for `StatusUpdated`, `ScanResultUpdated`, `AlignmentInfoUpdated`, and `CaptureRegionAligned` events.
- Refactor signal emission sites to send payload objects instead of raw kwargs.
- Update listeners in GUI, web, and state modules to accept typed payloads.
- Add tests that validate event payload compatibility.

### Out of scope
- Using a full event sourcing framework.
- Over-engineering with generic event envelopes unless needed for future requirements.

## Success Criteria
- A small set of event data classes exists and is used consistently across internal event dispatch.
- Signal consumers no longer rely on ad hoc kwargs for core event types.
- Event payloads are documented in the shared event module or PRD.
- Existing behavior is preserved and tests cover payload typing.

## Quality Requirements
- Make event payload classes immutable where practical.
- Keep payload definitions simple and focused on the event semantics.
- Do not use `Any` for core event payload properties.
- Prefer explicit fields over generic dictionaries.

## Implementation Checklist
- [ ] Define typed payload classes for major internal events.
- [ ] Update `status_updated`, `scan_result`, `alignment_info`, and any new alignment events to use payload objects.
- [ ] Refactor listeners to accept typed payloads.
- [ ] Add tests for payload correctness and listener compatibility.
