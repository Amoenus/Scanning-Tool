# Concerns Architecture

This document defines the **per-concern architecture** that underpins ORCA's event-driven design. It is the structural counterpart to the UX vision in `ux-vision.md`. Read them together.

## Why concerns and not UIs

ORCA renders multiple UIs serving multiple roles (see `ux-vision.md`). A naive approach to multi-UI would treat each UI as a peer and chase "feature parity" between them. This produces silent drift: a feature ships in Tk, the Qt PoC quietly lacks it, and nobody notices until a user reports it.

The structural alternative is to define the application as a set of **concerns** — bounded slices of capability with their own action vocabulary, signal vocabulary, and read model. UIs are composed of concerns they choose to render. Parity is verified per concern, not per UI.

This decouples three things that the current codebase mixes:

1. **What the application can do** (concerns and their contracts).
2. **What a given UI surfaces of that capability** (UI manifest).
3. **How a given toolkit renders it** (Tk vs. Qt vs. HTML).

Drift between UIs becomes a manifest fact ("Qt PoC does not yet claim the EditMode concern") rather than silent absence.

## The five concerns

ORCA's surface area decomposes into five concerns. Each is shaped the same way: a set of **actions** (commands flowing in), a set of **signals** (events flowing out), and an optional **read model** (the canonical state any UI rendering this concern projects from).

| Concern | Actions in | Signals out | Read model |
|---|---|---|---|
| **Configuration** | UpdateCaptureRegion, UpdateAnchorRegion, UpdateAnchorOffset, UpdateAlignmentPollInterval, UpdateAnchorThreshold, UpdateContinuousCaptureInterval, UpdateResultDisplayOffset, ChooseLabelColor, ApplyOllamaHost, ApplyOllamaModel, UseLocalhost, RestartOllama, ToggleAutoAlignment, ToggleCaptureBorder, ReloadAnchorTemplates, OpenAnchorDirectory, SaveConfig | config_changed, config_persisted, config_load_failed | `ConfigSnapshot` (immutable view of current effective config) |
| **Runtime status** | (none — read-only concern) | service_health_changed, alignment_status_changed, ollama_status_updated, ollama_readiness_changed | `ServiceStatus` (aggregate of Ollama health, alignment lock state, capture-pipeline state) |
| **Event log** | (none — append-only stream) | event_log_emitted (curated semantic events), raw_log_emitted (loguru passthrough, optional) | Recent buffer of `LogEntry` records |
| **Scan result** | SingleScan, ToggleContinuousCapture | scan_requested, scan_started, scan_completed, scan_failed | `LatestScan` (most recent `ScanResult` with metadata) |
| **Edit mode** | EnterEditMode, ExitEditMode, SelectRegion, NudgeRegion, DragRegion, ResetRegion, LockRegion, ToggleEditModeToolbar | edit_mode_changed, region_drafted, region_committed | `EditModeState` (active region, draft values, toolbar visibility) |

These are the five concerns identified in the UX vision. Future concerns will be added as the application grows — likely candidates: **Presets** (PRD 21), **Hotkeys** (PRD 24), **Onboarding wizard** (PRD 20).

## Concern shape

Every concern has the same three-part shape:

### Actions in (commands)

Actions are commands that *request* a change. They are imperative, named, and live in a per-concern namespace (see the namespaced-vocabularies ADR). Actions are published by UIs and consumed by services.

A concern that has no actions (Runtime status, Event log) is a read-only concern — UIs can render its read model but cannot drive it.

### Signals out (events)

Signals describe state changes that have *already happened*. They are past-tense, named, and live in a per-concern namespace. Signals are published by services and consumed by UIs (and other services).

Signals carry typed payloads (see PRD 13: typed event payloads). A signal vocabulary is part of the concern's public contract.

### Read model

The read model is the canonical state shape that any UI rendering this concern projects. It is immutable (snapshots) and serializable (so the same shape can flow through in-process signals and out through HTTP/SSE to the web overlay).

A concern's read model is updated by signals and queried by UIs at render time. UIs may keep their own derived state (selected widget, toggle positions) but they should not maintain shadow copies of the read model.

## UI manifests

Each UI declares which concerns it claims, in a per-UI manifest. Conceptually:

```
Tk control panel:
  - Configuration       (publish actions, render read model)
  - Runtime status      (render read model)
  - Event log           (render read model)
  - Scan result         (publish SingleScan/ToggleContinuousCapture, render read model)
  - Edit mode           (render read model — slider sync only, no drag)

In-game overlay:
  - Scan result         (render read model)
  - Edit mode           (publish all actions, render read model)
  - Configuration       (publish via edit-mode actions, no direct controls)

Web overlay:
  - Scan result         (render read model only)

Qt PoC (initial):
  - Configuration       (publish actions, render read model)
  - Runtime status      (render read model)
```

A UI claiming a concern commits to satisfying that concern's contract. A UI not claiming a concern is honestly absent — not a regression.

The manifest is machine-readable. A test verifies that every claimed concern has the required handlers wired. A test verifies that every signal in the bus has at least one publisher and that every action has at least one handler.

## Parity is per-concern, declared in manifests

If two UIs both claim the Configuration concern, they must both satisfy the Configuration conformance suite. The suite is a set of scripted scenarios that exercise the concern through its actions and assert its signals fire and its read model updates correctly. The suite runs parameterized over every UI claiming the concern.

This gives us:

- **Per-concern conformance tests** that catch silent drift the moment it appears.
- **Honest gaps** — a UI not claiming a concern is fine; a UI claiming it must satisfy it.
- **A natural growth model** — a new concern adds a manifest field and a conformance suite; UIs opt in.

See the per-concern parity ADR.

## Vocabulary namespacing

Today, `UiActionType` is a single flat enum mixing config writes (`UPDATE_CAPTURE_REGION`), runtime commands (`SINGLE_SCAN`, `RESTART_OLLAMA`), and overlay tweaks (`CHOOSE_LABEL_COLOR`). Three concerns share one namespace.

The structural fix is to split the action enum and the signal module by concern:

```
state/
  actions/
    config.py        # ConfigAction enum
    runtime.py       # RuntimeAction enum
    edit_mode.py     # EditModeAction enum
    scan.py          # ScanAction enum
  signals/
    config.py        # config_changed, config_persisted, ...
    runtime.py       # service_health_changed, ...
    event_log.py     # event_log_emitted, raw_log_emitted
    scan.py          # scan_started, scan_completed, scan_failed
    edit_mode.py     # edit_mode_changed, region_drafted
  read_models/
    config.py        # ConfigSnapshot
    runtime.py       # ServiceStatus
    event_log.py     # LogBuffer
    scan.py          # LatestScan
    edit_mode.py     # EditModeState
```

A concern's vocabulary is therefore one action module + one signal module + one read-model module. Importing the namespace says "I touch this concern."

See the namespaced-vocabularies ADR and PRD 16.

## Read models are also wire payloads

A non-obvious benefit of the read-model-per-concern shape: the same model is what the SSE stream serializes for the web overlay. The in-game overlay subscribes to in-process signals; the web overlay subscribes to the SSE stream. Both consume the same `LatestScan` shape. Drift between them becomes impossible by construction — they share the model, not the rendering.

This is the EDA story applied end-to-end. See PRD 22 for the SSE migration.

## Polling is a concern-internal implementation detail

The push-flow ADR formalizes the rule: UIs do not poll. But some sources cannot push — Ollama health is the canonical example.

The structural answer: each concern owns its own polling adapter (if it needs one), and the adapter publishes signals. Polling lives once, behind a named adapter, hidden from UIs. The Runtime status concern has an `OllamaHealthPoller` that publishes `ollama_status_updated` and `ollama_readiness_changed`; UIs see only the signals.

Continuous scan is structurally similar: the Scan result concern owns a scheduler that publishes `scan_requested` at the configured interval. UIs see scan lifecycle signals; they don't time anything.

## Conformance test pattern

A conformance test is a scenario scripted against a concern's contract:

1. Construct the concern's services (with test doubles where appropriate).
2. Construct the UI under test, claiming the concern.
3. Drive the UI to publish a known action (or simulate an upstream signal).
4. Assert the expected signals fire with expected payloads.
5. Assert the read model reflects the expected state.

The test is parameterized over `[tk, qt, web]` (or whichever UIs claim the concern). Tk runs headless. Qt runs with `QT_QPA_PLATFORM=offscreen`. Web runs against the Flask test client.

A typical Configuration scenario:

```
Given: a clean ConfigSnapshot
When:  the UI publishes UpdateCaptureRegion(left=100, top=200, width=300, height=400)
Then:  config_changed fires with the new region
And:   ConfigSnapshot.capture_region == CaptureRegion(100, 200, 300, 400)
```

The same test runs for every UI in the manifest. A new UI plugs into the parametrize list. A UI that claims a concern but fails its conformance suite is a regression caught at CI time.

## Concerns that cross other concerns

Some user-facing capabilities span multiple concerns. Edit mode is the canonical example: it publishes `EditModeAction` events, but those translate into `ConfigAction` writes (a region drag commits a `UPDATE_CAPTURE_REGION`).

The pattern: a concern may *use* another concern's actions. Edit mode is allowed to publish Configuration actions. It is not allowed to write to the Configuration read model directly. This keeps the Configuration concern in charge of its own state and lets edit mode focus on the interaction layer.

Crossings happen at the action layer, never at the read model. If two concerns need to share a read model, that is a sign the boundary is wrong.

## Relationship to existing PRDs

This architecture builds on previously accepted decisions and PRDs:

- **PRD 12 (event bus abstraction)** — concerns publish through the event bus, not directly to `blinker.Signal`.
- **PRD 13 (typed event payloads)** — concern signals carry typed payloads.
- **PRD 15 (capture command lifecycle)** — the Scan result concern's actions and lifecycle signals are the formalization of capture lifecycle events.
- **Decision 8 (use blinker)** — blinker remains the in-process implementation; the concern shape is independent of the bus library.

PRD 16 in this batch operationalizes the concern split. PRDs 17–24 are concrete features that consume this architecture.

## Out of scope

- **Cross-process / distributed event delivery.** The concern shape is in-process. If we ever need cross-process (e.g. companion app on a different machine driving config), revisit then.
- **Replacing blinker.** The concern shape is library-independent but does not require a swap.
- **Removing existing flat `UiActionType`** in one pass. PRD 16 sequences the migration.
