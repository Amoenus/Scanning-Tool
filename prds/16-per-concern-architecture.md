# PRD: Per-Concern Architecture

## Purpose
Operationalize the per-concern decomposition described in `architecture/concerns-architecture.md`: split the flat `UiActionType` enum and the flat signals module into per-concern namespaces, define read models per concern, introduce per-UI manifests, and add per-concern conformance tests. This is the foundational structural refactor that unlocks PRDs 17–24.

## Problem Statement
ORCA renders multiple UIs (Tk control panel, in-game overlay, Flask web overlay, Qt PoC) but has no structural mechanism to enforce that they stay coherent. The action vocabulary (`UiActionType`) and signal vocabulary (`state.signals`) are flat — every UI sees everything, and there is no machine-readable record of which UI implements which capability. As surfaces multiply, this guarantees silent drift.

The decision records `2026-04-29-per-concern-parity-over-per-ui-parity` and `2026-04-29-namespaced-action-and-signal-vocabularies` resolve the architectural direction. This PRD specifies the implementation work.

## Goals
- Decompose ORCA's surface area into the five concerns identified in `architecture/concerns-architecture.md`: Configuration, Runtime status, Event log, Scan result, Edit mode.
- Split actions into per-concern enums under `state/actions/`.
- Split signals into per-concern modules under `state/signals/`.
- Define an immutable read model per concern under `state/read_models/`.
- Introduce a per-UI manifest mechanism declaring which concerns each UI claims.
- Add a conformance test framework that exercises each concern through its contract, parameterized over the UIs that claim it.
- Keep the application working at every step — no big-bang switchover.

## Scope
### In scope
- Creation of `state/actions/`, `state/signals/`, `state/read_models/` package structure.
- Per-concern action enums (`ConfigAction`, `RuntimeAction`, `EditModeAction`, `ScanAction`).
- Per-concern signal modules with re-exports for compatibility during migration.
- Per-concern read-model dataclasses (immutable snapshots).
- A `ui_manifest.py` (or similar) per UI declaring claimed concerns.
- A conformance test base class and at least one scenario per concern.
- Migration of existing publishers and handlers to the new namespaces.
- Removal of the flat `UiActionType` enum once all call sites are migrated.

### Out of scope
- Replacing `blinker` as the in-process bus.
- Rewriting service implementations (only their import lines and event names).
- New features (covered by PRDs 17–24).
- The Edit mode and Presets concerns' full implementation — only their vocabulary and read models are introduced here.

## Success Criteria
- All actions live under `state/actions/<concern>.py`.
- All signals live under `state/signals/<concern>.py`.
- Each concern has an immutable read model in `state/read_models/<concern>.py`.
- Each UI under `gui/tk/`, `gui/qt/`, and `web/` has a manifest declaring its claimed concerns.
- A conformance test runs per concern, parameterized over claiming UIs, and passes for all current UIs.
- The flat `UiActionType` enum is removed.
- The application launches, scans, and updates the web overlay with no behavior change observable to a user.

## Quality Requirements
- Read models are immutable (frozen dataclasses or equivalent).
- Action and signal names are stable strings — they appear in tests and (eventually) on the SSE wire.
- No business logic moves into the action/signal/read-model packages; these are vocabulary only.
- Cross-concern references happen at the action layer, never at the read-model layer.
- Conformance test scenarios live near the concern they test, not in a single mega-file.

## Operation Model
1. Add the new package structure with empty per-concern modules.
2. Define one concern's vocabulary at a time, starting with **Scan result** (smallest surface area, well-bounded).
3. For each concern:
   1. Define actions, signals, and read model.
   2. Migrate publishers and handlers from the flat namespace.
   3. Add a manifest entry for each UI that handles the concern.
   4. Write conformance scenarios.
4. Once all five concerns are migrated, remove the flat `UiActionType` enum.

Suggested concern order: Scan result → Runtime status → Event log → Configuration → Edit mode (Edit mode last because it depends on Configuration).

## Implementation Approach
- Create a `ConcernManifest` dataclass with fields like `claimed_concerns: frozenset[str]`, `published_actions: frozenset[ActionType]`, `subscribed_signals: frozenset[SignalName]`.
- Each UI provides a module-level `MANIFEST: ConcernManifest`.
- A pytest fixture loads all manifests and parameterizes conformance scenarios over the claiming UIs.
- A test asserts: every action enum member has at least one handler; every signal has at least one publisher; every UI's claimed concerns are matched by its declared actions and subscriptions.

## Risks and Mitigations
- **Risk:** migration touches a lot of files at once, increasing merge risk.
  - Mitigation: per-concern migration; merge each concern as a self-contained PR.
- **Risk:** conformance tests become a maintenance burden.
  - Mitigation: keep scenarios minimal and per-concern; do not test integrations between concerns in the conformance suite.
- **Risk:** read models drift from publishers.
  - Mitigation: each signal handler that updates a read model lives next to the read-model definition; a test asserts the handler is registered for the signal.

## Implementation Checklist
- [ ] Create `src/scanning_tool/state/actions/` package with placeholder modules per concern.
- [ ] Create `src/scanning_tool/state/signals/` package (refactor existing flat module into per-concern submodules).
- [ ] Create `src/scanning_tool/state/read_models/` package with one dataclass per concern.
- [ ] Migrate Scan result vocabulary; update publishers and handlers.
- [ ] Migrate Runtime status vocabulary; absorb existing Ollama and alignment status signals.
- [ ] Migrate Event log vocabulary; introduce `event_log_emitted` (curated) and `raw_log_emitted` (loguru passthrough).
- [ ] Migrate Configuration vocabulary; replace flat `UiActionType` config members.
- [ ] Migrate Edit mode vocabulary (placeholder until PRD 17 implements behavior).
- [ ] Define `ConcernManifest` dataclass.
- [ ] Add `MANIFEST` to Tk control panel, Qt PoC, in-game overlay, web overlay.
- [ ] Write per-concern conformance test base class.
- [ ] Add at least one conformance scenario per concern.
- [ ] Add structural assertions (every action handled, every signal published, every claimed concern realized).
- [ ] Remove the flat `UiActionType` enum.
- [ ] Update `architecture/concerns-architecture.md` if implementation reveals shape adjustments.
- [ ] Update `prds/00-overview.md` to reference per-concern model.
