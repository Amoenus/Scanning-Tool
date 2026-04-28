# PRD: Alignment Service Signal Decoupling

## Purpose
Separate auto-alignment business logic from presentation-specific UI signal emissions so the service layer remains focused on domain behavior and not on GUI wiring.

## Problem Statement
`AlignmentService` currently emits UI-specific signals directly from within its domain logic. This couples alignment calculations to presentation helpers such as capture slider synchronization and overlay updates, making the service less reusable, harder to test, and harder to evolve.

## Goals
- Keep alignment business logic inside `services/alignment_service.py` and domain models.
- Emit domain-level events for alignment outcomes instead of UI-only signals.
- Let presentation adapters subscribe to alignment change events and translate them into UI synchronization actions.
- Preserve existing alignment behavior while improving modularity.

## Scope
### In scope
- Refactor `AlignmentService._apply_alignment()` to publish a generic alignment event.
- Remove direct `sync_capture_sliders_signal` and `update_capture_overlay_region_signal` calls from `AlignmentService`.
- Define a domain event such as `capture_region_aligned` or `alignment_applied` in a shared signals module.
- Update UI adapters (Tk, web, overlay state) to subscribe to that new event instead of service internals.

### Out of scope
- Changing the alignment algorithm or capture region math.
- Reworking alignment configuration data models.
- Replacing the underlying signal library.

## Success Criteria
- `AlignmentService` no longer imports or sends `sync_capture_sliders_signal` or `update_capture_overlay_region_signal`.
- A new event signal is emitted for alignment updates with a clear payload type.
- UI components still receive notifications when the capture region changes.
- Tests verify that alignment logic is decoupled from UI signals and that UI adapters handle the new event.

## Quality Requirements
- Use explicit event data classes for alignment events if the payload is non-trivial.
- Keep the new event in the shared `state/signals.py` or an adjacent domain event module.
- Prefer constructor injection or adapter interfaces for wiring event subscribers.
- Document the event contract in both service and UI modules.

## Implementation Checklist
- [ ] Define `alignment_applied` or equivalent event in shared signals.
- [ ] Update `AlignmentService` to emit the new event instead of UI-specific signals.
- [ ] Add adapter-level listeners in GUI/web layers for the new event.
- [ ] Add tests covering the refactor and validating decoupling.
- [ ] Update architecture docs or PRD references if needed.
