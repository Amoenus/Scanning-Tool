# PRD: Capture Command Lifecycle Events

## Purpose
Make capture orchestration explicit through command and lifecycle events so the capture workflow is more understandable, testable, and extensible.

## Problem Statement
Capture workflows are currently managed imperatively inside `CaptureUseCase.capture_once()`. Status updates, alignment, OCR, and scan result reporting are mixed together with no clear command/event boundary, which reduces transparency and makes extensions harder.

## Goals
- Treat user-facing capture operations as explicit commands and lifecycle events.
- Publish events such as `CaptureRequested`, `CaptureStarted`, `CaptureCompleted`, and `CaptureFailed`.
- Let listeners handle status updates, result reporting, and post-capture behavior without being tightly coupled to `CaptureUseCase` internals.

## Scope
### In scope
- Define capture command/event types in a shared event module.
- Refactor `CaptureUseCase` to publish lifecycle events at clear stages.
- Update status reporting, logging, and web/UI observers to consume these events.
- Preserve the existing one-shot capture and continuous capture behavior.

### Out of scope
- Changing the capture engine or OCR provider.
- Adding multi-user or distributed capture semantics.

## Success Criteria
- Capture lifecycle events are emitted at key points in the flow.
- Status updates and scan result notifications can be derived from the new events rather than from lower-level implementation details.
- The command lifecycle is documented and testable.
- Existing capture behavior remains unchanged from the user perspective.

## Quality Requirements
- Keep lifecycle event definitions explicit and immutable.
- Avoid coupling the capture workflow to any presentation layer.
- Use the event bus abstraction if it is available from the other PRD work.
- Ensure events are emitted consistently for both success and failure cases.

## Implementation Checklist
- [ ] Define capture command/lifecycle event types.
- [ ] Refactor `CaptureUseCase.capture_once()` to publish the new events.
- [ ] Update status and result reporting to consume lifecycle events.
- [ ] Add tests verifying capture lifecycle event emission.
- [ ] Document the capture event lifecycle in architecture docs.
