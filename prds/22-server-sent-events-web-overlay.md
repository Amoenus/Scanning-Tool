# PRD: Server-Sent Events for the Web Overlay

## Purpose
Replace the web overlay's polling/auto-refresh loop with Server-Sent Events (SSE) so the companion web UI consumes the same push signals as the in-game overlay. This is the EDA story applied end-to-end and removes the last polling loop the application does not strictly need.

## Problem Statement
The web overlay currently auto-refreshes on each scan via repeated HTTP requests against the embedded Flask server. This works but has three downsides:

- The browser polls regardless of whether new data exists — wasted requests.
- The companion view can lag behind the in-game overlay by one polling interval.
- The web overlay does not participate in the application's event-driven architecture; it has its own pull-based model.

The push-flow ADR formalizes the rule: UIs subscribe to push signals and do not poll. The web overlay is a UI, so it should follow the same rule. SSE is the simplest standard mechanism that lets a browser subscribe to a server-pushed event stream over a single HTTP connection, with automatic reconnect.

## Goals
- Add an SSE endpoint to the Flask web server that streams Scan result concern events.
- Update the web overlay HTML to consume the SSE stream via `EventSource`.
- Remove the existing polling/auto-refresh in the web overlay.
- Have the web overlay reflect new scans within milliseconds of the in-process signal firing.
- Serialize the same `LatestScan` read model the in-game overlay consumes — no parallel data shape.

## Scope
### In scope
- A `/events` (or similarly named) SSE endpoint on the Flask server.
- A bridge from in-process `scan_completed` / `scan_failed` / `scan_started` signals to the SSE stream.
- A serializer that converts `LatestScan` to a JSON payload identical to what the in-game overlay renders from.
- Updated `templates/overlay.html` consuming `EventSource`.
- Heartbeat / keep-alive at the SSE layer to survive proxies and idle disconnects.
- Server-side handling of multiple connected clients (multiple devices viewing the same overlay).

### Out of scope
- Authentication / per-user streams (the web overlay is local-network only).
- Streaming Configuration or Edit-mode events (the web overlay is read-only and scan-result-only by design — see `architecture/ux-vision.md`).
- Migrating the web server to async (Flask + threaded SSE is sufficient at the expected client count).
- Streaming Runtime status to the web overlay (consider in a future PRD if the companion role grows to need health visibility).

## Success Criteria
- The web overlay receives new scan results without polling.
- A new scan in-game appears in a connected browser within 250ms (typical local network).
- The browser automatically reconnects after network blip without page refresh.
- Multiple browsers connected simultaneously all receive updates.
- The SSE payload is the JSON serialization of the same `LatestScan` read model the in-game overlay uses.
- Web overlay conformance scenarios pass against the SSE stream (using Flask test client with EventSource semantics).

## Quality Requirements
- The SSE bridge subscribes to in-process signals via the event bus abstraction (PRD 12), not by importing `state.signals` directly.
- Payload serialization happens in one place; the in-game overlay reads the same shape.
- The SSE stream coalesces rapid bursts (continuous-scan mode at fast interval) per the push-flow ADR.
- The endpoint sets correct `Content-Type: text/event-stream` and disables proxy buffering (`X-Accel-Buffering: no`).
- Server-side resources (per-client queue) are bounded; slow clients are dropped, not buffered indefinitely.

## Operation Model
1. Browser opens the web overlay page; the page opens an `EventSource` against `/events`.
2. The Flask server registers a per-client queue and subscribes it to scan-result signals via the bridge.
3. When a scan completes in-process, `scan_completed` fires; the bridge serializes `LatestScan` and pushes to all client queues.
4. The browser's `EventSource` handler receives the message and updates the DOM.
5. On disconnect (network or client close), the per-client queue is cleaned up; the browser auto-reconnects.

## Implementation Approach
- Add an SSE bridge service (`web/sse_bridge.py`) that subscribes to scan-result signals and maintains a registry of per-client queues.
- Add a `/events` route in the Flask app that streams from the per-client queue with appropriate headers.
- Add a JSON serializer for `LatestScan` (live in `state/read_models/scan.py` or equivalent).
- Update `templates/overlay.html` to consume `EventSource` and apply DOM updates on each event.
- Remove the polling/auto-refresh code from the template.

## Risks and Mitigations
- **Risk:** Flask's threaded SSE doesn't scale beyond a handful of clients.
  - Mitigation: expected concurrent clients is small (one player + maybe a friend); document limit; revisit if needed.
- **Risk:** corporate firewalls or unusual network setups break SSE.
  - Mitigation: keep a JSON status endpoint as a fallback (server can still respond to a one-shot HTTP poll if a client requests it); document the fallback.
- **Risk:** signal subscriber lifetime mismanaged on client disconnect, leading to leaks.
  - Mitigation: explicit subscribe/unsubscribe paired with the request lifecycle; tests assert no leaked subscribers after disconnect.

## Implementation Checklist
- [ ] Define the JSON serialization for `LatestScan`.
- [ ] Implement the SSE bridge service subscribing to scan-result signals.
- [ ] Add `/events` route to the Flask app.
- [ ] Update `templates/overlay.html` to use `EventSource`.
- [ ] Remove existing polling/auto-refresh from the template.
- [ ] Add heartbeat / keep-alive.
- [ ] Add server-side connection limits and slow-client handling.
- [ ] Write conformance scenarios for the web overlay against the SSE stream.
- [ ] Document the SSE endpoint in `architecture/concerns-architecture.md`.
- [ ] Update `README.md` to mention the push behavior.
