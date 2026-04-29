# PRD: Curated Event Log

## Purpose
Introduce a user-facing event log that emits semantic, stable, human-readable events ("Scanned ✓ TIN (Quantum)", "Auto-align lost lock", "Ollama reconnected") above the raw loguru stream. The curated log is the user-visible surface; raw loguru remains available behind a "Diagnostics" toggle for developers and advanced troubleshooting.

## Problem Statement
ORCA is launched from a console, so loguru output is incidentally visible to the user. Loguru output is shaped for developers — module names, log levels, structured fields, occasional tracebacks. This is the wrong surface for a player who wants to know "did the scan work?" or "why did alignment fail?"

We need a clean separation:
- Players and operators should see a curated stream of semantic events.
- Developers and troubleshooters should be able to access the raw loguru stream when needed.

The curated stream is its own concern (Event log) with its own signal vocabulary. It is *not* a filtered view of loguru — it has independent wording chosen for end users, stable across log-format changes, and testable.

## Goals
- Define an `event_log_emitted` signal that carries semantic events.
- Build a curated event catalog covering scan lifecycle, alignment lifecycle, Ollama lifecycle, configuration changes, and edit-mode lifecycle.
- Render the curated event log in the control panel as a scrollable timeline (default visible).
- Render raw loguru output behind a "Show diagnostics log" toggle (default hidden).
- Ensure curated events are testable independently of loguru formatting.

## Scope
### In scope
- `EventLogEntry` dataclass: timestamp, level (info/warn/error), category (scan/alignment/ollama/config/edit), headline, optional detail.
- `event_log_emitted` signal in the Event log concern.
- Service-side emission of curated events at well-defined moments (scan completed, scan failed, alignment lost, alignment recovered, Ollama disconnected, Ollama reconnected, config saved, preset switched, edit mode entered/exited).
- A control panel section rendering the most recent N entries with category filters.
- A diagnostics toggle that reveals the raw loguru sink in the same window.
- A loguru sink that re-emits selected log records as `raw_log_emitted` signals (for the diagnostics toggle).

### Out of scope
- Persisting the event log to disk (current loguru file sink remains as-is).
- Search or full-text query over the log.
- Remote log shipping.
- Rendering the curated log in the in-game overlay (the overlay has the bare scan-result surface; long-form events live in the control panel).

## Success Criteria
- Every concern that can emit a user-relevant event publishes through `event_log_emitted` with a stable headline.
- The control panel's curated log shows the most recent events without showing loguru module/level chrome.
- The diagnostics toggle reveals the raw loguru output in the same window when the user wants it.
- Event headlines are stable across releases — log-format changes do not break user-facing wording.
- Conformance scenario verifies that emitting `scan_completed` results in an `event_log_emitted` entry with the expected category and headline.

## Quality Requirements
- Curated event headlines are short (under 80 characters) and player-readable.
- Detail (long form) is optional and only rendered on click/expand.
- The log buffer is bounded (e.g. last 500 entries) — no unbounded memory growth.
- Curated events are emitted from the originating service, not derived in a presentation layer.

## Operation Model
1. A service reaches a noteworthy moment (scan completed, alignment lost, Ollama reconnected).
2. The service publishes the relevant concern signal (e.g. `scan_completed`).
3. An Event-log adapter subscribes to all relevant concern signals and translates them into `EventLogEntry` records, then publishes `event_log_emitted`.
4. The control panel's event-log section appends the entry to its scrollable view.
5. If the diagnostics toggle is on, the raw loguru sink also emits `raw_log_emitted`, which renders in the diagnostics pane.

## Implementation Approach
- Define `EventLogEntry`, `event_log_emitted`, and `raw_log_emitted` per PRD 16.
- Implement a single `EventLogTranslator` service that subscribes to `scan_completed`, `scan_failed`, `alignment_lost`, `alignment_recovered`, `ollama_status_updated`, `config_persisted`, `edit_mode_changed`, etc., and emits curated entries.
- Implement a loguru sink that filters by level (default WARNING and above) and re-emits as `raw_log_emitted`. Filter is configurable.
- Add an `EventLogSection` to the Tk control panel (new section, default expanded, top of the panel under Runtime Status). The diagnostics toggle reveals an additional pane below.
- Mirror in Qt control panel.

## Risks and Mitigations
- **Risk:** translation logic becomes a god object.
  - Mitigation: per-concern translator submodules (`translate_scan.py`, `translate_alignment.py`, ...).
- **Risk:** event headlines drift from the catalog.
  - Mitigation: catalog them as constants in a single module; tests assert published events match the catalog.
- **Risk:** the curated log feels noisier than loguru if too many events are emitted.
  - Mitigation: explicitly enumerate which moments emit; add per-category filter in the UI.

## Implementation Checklist
- [ ] Define `EventLogEntry` dataclass and the `event_log_emitted` / `raw_log_emitted` signals.
- [ ] Catalog curated event headlines per category in a single constants module.
- [ ] Implement `EventLogTranslator` subscribing to scan/alignment/ollama/config/edit signals.
- [ ] Add a loguru sink that re-emits as `raw_log_emitted` (filterable by level).
- [ ] Build the Tk `EventLogSection` (scrollable timeline + filter + diagnostics toggle).
- [ ] Mirror in Qt control panel.
- [ ] Add Event log conformance scenarios (one per category).
- [ ] Document the event catalog in `architecture/concerns-architecture.md`.
- [ ] Update `ux-vision.md` if implementation refines the surface design.
