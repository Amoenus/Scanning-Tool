# PRD: Actionable Status Badges

## Purpose
Extend the existing color-coded status badges in the control panel so red (failure) badges become click-to-act CTAs that surface the failure detail and one or more remediation actions. Green badges remain passive indicators. The badge widget gains a second mode rather than being replaced.

## Problem Statement
The Runtime Status section uses compact color-coded badges as a glanceable health indicator — green for "everything is fine," red for "something is wrong." This is the right design for the happy path: users want a one-glance "is it working?" answer.

The gap is that red badges are read-only. "Auto align: Active (searching)" tells the user *that* alignment is failing but not *what to do*. "Ollama status: Waiting" does not tell the user whether to wait, restart, or check the host. The user has to consult the readme, the console log, or trial-and-error.

Today's badges therefore describe state but do not help the user recover. The fix is not to remove badges (color-coded glanceability is the right design) but to give them a second mode when red.

## Goals
- Keep the visual design and glanceable color coding of the current badges.
- When a badge is in a failure state (red or amber), make it interactive — clicking or hovering reveals failure detail and one or more remediation actions.
- Define the failure-mode shape per concern: each red state has a description, a probable cause, and at least one remediation action.
- Make remediation actions one click away from the badge — no navigating to other panels or reading the readme.

## Scope
### In scope
- Add a `BadgeState` model: `level` (ok / warn / fail), `headline` (current badge text), `detail` (human description of the failure), `remediations` (list of named actions).
- Extend the existing `_create_badge` helper to render a popover/tooltip for non-OK states.
- Define remediation action templates for each known failure mode in Runtime status: alignment-lost, alignment-low-score, ollama-unreachable, ollama-model-missing, capture-region-invalid.
- Wire each remediation to its corresponding `RuntimeAction` or `ConfigAction`.
- Mirror the same model in the Qt control panel UI (when present).

### Out of scope
- Replacing the badge layout or color scheme.
- Adding new failure modes that the underlying services do not currently detect.
- Surfacing badges in the in-game overlay (the overlay has its own minimal status surface; this PRD is control-panel only).
- Localization of remediation text.

## Success Criteria
- Every existing badge that can enter a failure state has a defined `BadgeState.remediations` list.
- Hovering or clicking a red badge surfaces the failure detail in under one second.
- At least one remediation per failure mode can be triggered without leaving the badge popover.
- Green badges have no popover and behave exactly as today.
- The Tk and Qt control panels render identical badge state (verified via Runtime status conformance scenarios).

## Quality Requirements
- Badge state changes flow through the Runtime status concern's signals — no direct queries.
- Remediation actions emit standard concern actions; they do not call services directly.
- Popover content is keyboard-accessible (Tab to badge, Enter to open, arrows to select remediation).
- No popover persists when the badge returns to OK.

## Operation Model
1. A failure detected by the relevant service (alignment, Ollama health, capture pipeline) publishes a status change signal with payload including detail and probable remediation hints.
2. The Runtime status concern updates `ServiceStatus.badges[name] = BadgeState(level=fail, headline=..., detail=..., remediations=[...])`.
3. The control panel's badge listener re-renders the badge with red color.
4. User clicks/hovers the badge. Popover renders the detail and remediation buttons.
5. User clicks a remediation. The badge widget publishes the corresponding action (e.g. `ConfigAction.ReloadAnchorTemplates`, `RuntimeAction.RestartOllama`).
6. When the failure clears, `ServiceStatus.badges[name].level` returns to `ok`; the popover dismisses.

## Implementation Approach
- Define `BadgeState` and `Remediation` dataclasses in `state/read_models/runtime.py`.
- Map each known failure into a `BadgeState` template in a `runtime_failure_modes.py` helper. Centralizing the templates keeps remediation copy and action wiring in one place.
- Extend `_create_badge` (and Qt equivalent) to accept a `BadgeState` provider and render the popover for non-OK states.
- Use Tk's `Toplevel` for the popover with `transient` and `overrideredirect` for a contextual appearance.

## Risks and Mitigations
- **Risk:** popover obscures other badges or window controls.
  - Mitigation: position popover at badge edge with collision detection against the panel boundaries.
- **Risk:** remediation actions mis-fire if the underlying state has changed since the badge was rendered.
  - Mitigation: badges are read from the read model at click time, not from cached state.
- **Risk:** scope creep — every diagnostic becomes a badge.
  - Mitigation: badges represent a fixed set of well-known service states; verbose diagnostics belong in the curated event log (PRD 19).

## Implementation Checklist
- [ ] Define `BadgeState` and `Remediation` dataclasses in `state/read_models/runtime.py`.
- [ ] Catalog known failure modes and their remediations in `runtime_failure_modes.py`.
- [ ] Extend Runtime status signals to carry `BadgeState` payloads where applicable.
- [ ] Update alignment, Ollama, and capture services to populate `BadgeState` on failure.
- [ ] Extend the Tk badge helper to render a popover for non-OK states.
- [ ] Add popover keyboard navigation.
- [ ] Wire remediation buttons to publish the appropriate concern actions.
- [ ] Mirror the implementation in the Qt control panel.
- [ ] Add Runtime status conformance scenarios for badge transitions.
- [ ] Document the failure-mode catalog in `architecture/concerns-architecture.md`.
