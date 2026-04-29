# Decision: Push-based event flow with isolated polling adapters

## Status
Accepted

## Context

ORCA already uses `blinker` for in-process event signaling (Decision 8) and is moving toward an explicit event bus abstraction (PRD 12) with typed payloads (PRD 13). The architectural intent has been "event-driven," but the rule has not been formalized: are UIs allowed to poll for state? Are services allowed to expose pull-based state in addition to publishing events?

Today there are de-facto polling loops in places — periodic Ollama status refreshes, the web overlay's auto-refresh on each scan. Each is independently justified, but the absence of a stated rule means "polling here was the easiest path" can creep in anywhere.

Some sources cannot push. Ollama's HTTP API does not stream health; we have to ask. That is a real constraint and any rule must accommodate it without compromising.

## Decision

**UIs subscribe to push signals. They do not poll.**

When a source cannot push, a single dedicated **polling adapter** lives inside the relevant concern. The adapter polls the source on a schedule, observes state, and publishes signals on change. UIs see only the signals.

Concretely:

- Ollama health belongs to the Runtime status concern. An `OllamaHealthPoller` (or equivalent) inside that concern polls Ollama and publishes `ollama_status_updated` and `ollama_readiness_changed` on change. UIs render the read model derived from these signals.
- Continuous scan belongs to the Scan result concern. A scheduler inside that concern publishes `scan_requested` at the configured interval. Scan lifecycle signals (`scan_started`, `scan_completed`, `scan_failed`) drive UIs. UIs do not time anything.
- The web overlay subscribes to scan signals via Server-Sent Events (PRD 22), not via repeated HTTP polls.

The rule is enforced at the concern boundary: a polling adapter is an internal implementation detail of one concern, and it is the only place polling is allowed.

## Consequences

- **UIs are simpler** — no timers, no debounce-the-poll logic, no "loading" state derived from "we asked but didn't get a response yet."
- **Polling lives once, named clearly** — `OllamaHealthPoller` is searchable and reviewable. Diffuse polling is easy to introduce, hard to find, and impossible to test.
- **The web overlay stops polling.** This is a meaningful UX win: the page reflects new scans within milliseconds and does not hammer the local Flask server.
- **Renderers must coalesce.** Push-everything is not "fire as fast as possible." High-frequency signals (drag events, fast continuous scans) must be coalesced at the rendering edge — latest value wins, drop intermediates, cap repaint at ~10 Hz. This belongs in the renderer; publishers should not guess consumer cadence.
- **Adding a new external source** that cannot push (e.g. a new OCR backend with no event API) means adding a polling adapter inside the relevant concern, not letting the polling leak into UIs.
- **Test scenarios become deterministic.** Conformance suites assert "publish signal X, expect read model Y" without involving the wall clock.
