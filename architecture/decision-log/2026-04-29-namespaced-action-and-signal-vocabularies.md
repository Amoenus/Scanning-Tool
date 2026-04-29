# Decision: Namespaced action and signal vocabularies per concern

## Status
Accepted

## Context

Today, `scanning_tool.gui.action_types.UiActionType` is a single flat enum that mixes actions belonging to multiple concerns:

- Configuration writes (`UPDATE_CAPTURE_REGION`, `UPDATE_ANCHOR_REGION`, `UPDATE_RESULT_DISPLAY_OFFSET`, `APPLY_OLLAMA_HOST`).
- Runtime commands (`SINGLE_SCAN`, `TOGGLE_CONTINUOUS_CAPTURE`, `RESTART_OLLAMA`).
- Overlay/edit-style actions (`CHOOSE_LABEL_COLOR`, `TOGGLE_CAPTURE_BORDER`, `TOGGLE_ANCHOR_OVERLAY`).

Similarly, `state.signals` carries a flat module of `blinker.Signal` instances mixing capture lifecycle, alignment, UI actions, overlay state changes, and Ollama status.

This works at small scale. As concerns multiply (Configuration, Runtime status, Event log, Scan result, Edit mode — see `architecture/concerns-architecture.md`), the flat namespace becomes:

- Hard to scope when declaring per-UI manifests ("which subset of `UiActionType` does the web overlay actually use?").
- Hard to evolve — every concern's vocabulary edits force a single shared enum/module.
- Hard to test — conformance suites for one concern have to filter the global enum.

## Decision

Split the action enum and the signal module by concern. Each concern owns:

- One action enum (e.g. `state.actions.config.ConfigAction`).
- One signal module (e.g. `state.signals.config`) with the concern's signals.
- One read-model module (e.g. `state.read_models.config`) with the immutable snapshot type.

A concern's vocabulary is therefore one action module + one signal module + one read-model module. Importing the namespace says "I touch this concern."

Layout:

```
state/
  actions/
    config.py        # ConfigAction
    runtime.py       # RuntimeAction
    edit_mode.py     # EditModeAction
    scan.py          # ScanAction
  signals/
    config.py
    runtime.py
    event_log.py
    scan.py
    edit_mode.py
  read_models/
    config.py
    runtime.py
    event_log.py
    scan.py
    edit_mode.py
```

The flat `UiActionType` enum is migrated and removed. PRD 16 sequences the migration.

## Consequences

- **Per-UI manifests become natural** — a UI declares "I publish ConfigAction and ScanAction; I subscribe to config, runtime, scan signals."
- **Concerns evolve independently** — adding a Presets concern adds `actions/presets.py` and `signals/presets.py`; existing concerns are not touched.
- **Conformance tests are scoped** — Configuration's conformance suite touches only Configuration's vocabulary.
- **Dead-code detection is easier** — a per-concern enum with no publishers or no handlers is a tighter signal than the same gap inside a 30-member flat enum.
- **The migration is non-trivial** — every existing publisher and handler is touched. PRD 16 specifies the order.
- **Cross-concern interactions become visible at the import line** — an Edit mode handler that publishes `ConfigAction.UpdateCaptureRegion` makes the dependency explicit. This is a feature, not a cost.
