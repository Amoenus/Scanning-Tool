# Decision: Per-concern parity over per-UI parity

## Status
Accepted

## Context

ORCA is moving from a single Tk control panel toward multiple UIs serving distinct user roles: a desktop control panel (Tk today, Qt being prototyped), an in-game overlay, a web companion overlay, and possibly future surfaces (tablet operator UI, headless CLI). See `architecture/ux-vision.md` for the role analysis.

A naive approach would treat each UI as a peer and chase strict feature parity between them. This produces silent drift: a feature ships in one UI, another quietly lacks it, and the gap is only discovered when a user reports it. It also misframes the problem — strict UI-to-UI parity is the wrong goal because the UIs serve different roles. The web companion *should not* expose "Save Config"; the in-game overlay *should not* expose Ollama host configuration.

We need a parity model that:

- Catches silent drift between UIs that claim to do the same thing.
- Allows honest, declared gaps where a UI intentionally omits a capability.
- Survives the addition of new UIs and new capabilities without becoming unmaintainable.

## Decision

Parity is enforced **per concern, not per UI**. The application is decomposed into a fixed set of concerns (see `architecture/concerns-architecture.md`), each with its own contract: actions in, signals out, optional read model. Each UI declares which concerns it claims, in a per-UI manifest. A UI that claims a concern must satisfy that concern's conformance suite; a UI that does not claim a concern is honestly absent from it, which is fine.

Conformance suites are scripted scenarios that exercise a concern through its contract and assert the expected signals fire and the expected read-model state is reached. The suite is parameterized over every UI claiming the concern.

## Consequences

- **Drift becomes a CI-time failure**, not a user-reported bug.
- **Honest gaps are first-class** — "Qt PoC does not yet claim the EditMode concern" is a manifest fact, not a regression.
- **Adding a new UI** is a manifest entry plus passing the conformance suites for the concerns it claims. The Qt PoC stops being a PoC and becomes a peer the moment it claims and passes a concern.
- **Adding a new capability** belongs to a single concern (or creates a new concern). Conformance suites grow with the concern; no per-UI catch-up checklist is needed.
- **The ceremony cost** is real: every new feature requires declaring its concern, writing a handler, and adding a conformance scenario. This is the price for not having silent drift.
- **The flat `UiActionType` enum is incompatible** with this model and is replaced by per-concern action namespaces (see the namespaced-vocabularies decision).
