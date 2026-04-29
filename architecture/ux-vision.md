# UX Vision

This document captures the UX vision for ORCA. It is a narrative anchor for the per-concern architecture (`concerns-architecture.md`), the decision records under `decision-log/`, and the PRDs under `../prds/`. It is intentionally opinionated; treat it as the framing that future PRDs and design choices should be judged against.

## Audience and roles

ORCA has three distinct user-facing roles, and the application is the union of surfaces that serve them. Roles are not users — one human can play several roles in a single session.

- **Operator** — the person setting the tool up, troubleshooting it, and tweaking how it behaves. Operates the desktop control panel. Reads diagnostics. Adjusts capture and anchor regions, picks templates, swaps Ollama models.
- **Player** — the person actively scanning deposits in the game. Wants the tool to be invisible until it has something to show, and instantly responsive when it does. Drives the in-game overlay through hotkeys.
- **Companion observer** — the person (often the same player on a second device) glancing at scan results without leaving the game. Consumes the web overlay. Read-only.

The same human typically plays operator first (during setup), then player (during gameplay), and may keep a phone or tablet on the desk as a companion observer.

## Surfaces

ORCA presents **five surfaces**, each serving a different role and rendering a different subset of the application's concerns.

| Surface | Role served | Primary purpose | Lifecycle |
|---|---|---|---|
| **Console window** | Operator (diagnostic) | Raw log output. Incidental to launch model — present because the app is launched from a console, not because it is spawned by the app. | Lives as long as the launching shell. User minimizes or ignores. |
| **Control panel** (Tk today, Qt tomorrow) | Operator | Home base for setup, inspection, and troubleshooting. Hosts configuration sections, runtime status, and (planned) curated event log. | Spawned at launch. User may minimize but can re-summon (planned tray icon). |
| **In-game overlay** | Player | Bare HUD. Shows the latest scan result on top of the game and provides the visual surface for spatial configuration via edit mode. | Spawned at launch. Always visible during gameplay. |
| **Web overlay** | Companion observer | Glanceable read-only view of the latest scan result for a second device (tablet/phone). Deliberately simpler than the in-game overlay — no edit mode, no diagnostics. | Hosted by the embedded Flask server. User opens in a browser or scans a QR. |
| **First-run wizard** (planned) | Operator (one-time) | 3-step calibration to replace the slider-wall onramp for new users. | Runs once on first launch; on demand thereafter. |

A surface is not a UI toolkit. The same toolkit (e.g. Tk) can render multiple surfaces. The same surface (e.g. in-game overlay) can in principle be rendered by different toolkits over time.

### Why we keep multiple UIs intentionally

The web overlay is *not* a degraded version of the in-game overlay — it is a different role's view of shared state. The web overlay is for the companion observer on a second device; the in-game overlay is for the player on the primary screen. Future surfaces (tablet operator UI, headless CLI, voice readout) are similarly justified by role, not by toolkit preference.

This is why **parity is enforced per concern, not per UI** — see `concerns-architecture.md` and the per-concern parity ADR.

## Application phases

ORCA operates in two phases that the UX must honor distinctly.

### Configuration phase (one-and-done)

The user adjusts capture region, anchor region, anchor template, label color, result-display offsets, Ollama model, and host. This phase is high-friction by nature (12+ spatial controls today). It is performed once per ship/resolution combination and rarely revisited.

**Design implication:** configuration controls should be hidden behind progressive disclosure (current "Advanced Settings" toggle is the right shape) and should not be the new-user onramp. Spatial controls should be primarily mouse-driven via in-game edit mode, with sliders as a fallback.

### Capture phase (per-second)

The user is in-game, aims at a deposit, hits a hotkey, and sees the result. This is the dominant interaction loop. Latency matters; visual noise matters; alt-tabbing breaks immersion.

**Design implication:** during capture phase, the in-game overlay is the only surface that must be glanceable. The control panel and console are background processes. The web overlay is a passive read-out for a separate device.

## The central UX pivot: in-game edit mode

This is the single most important UX commitment in the vision.

Star Citizen runs fullscreen. Alt-tabbing to the desktop control panel during gameplay is friction-heavy at best, broken at worst (exclusive fullscreen blanks the game, GPU pipeline stutters, etc.). Yet the user inevitably wants to nudge the capture box, swap presets, or check why auto-align failed *while in the game*.

The answer is **edit mode** — a hotkey-toggled state where the existing on-screen overlays (capture rectangle, anchor rectangle, info label) become directly manipulable with mouse and keyboard.

Edit mode behavior:

- Press a hotkey (default `F9`) to enter. Overlay rectangles become visually distinct (handles, dimension readout) and accept input. Game input is suppressed for the overlay's input scope.
- Mouse drags resize and reposition rectangles. Arrow keys nudge by 1 pixel. Shift+arrow nudges by 10 pixels. Tab cycles between rectangles (capture, anchor, info label position).
- A small contextual toolbar appears at the edge of the active rectangle: dimensions readout, lock toggle, reset, exit. Toolbar also exposes preset switcher (when implemented).
- All adjustments emit the same EDA actions used by the desktop sliders (`UPDATE_CAPTURE_REGION`, etc.). The desktop sliders update in real time via the same signals they already subscribe to. The control panel becomes a passive observer during edit mode, not the driver.
- Exiting edit mode returns input to the game.

**Why this matters:** edit mode changes the role of the desktop control panel from "primary configuration tool" to "diagnostic and inspection home base." The 12-slider wall stops being a usability problem because the new-user onramp is the wizard plus mouse-driven edit mode; sliders remain as a power-user fallback.

Edit mode also enables a class of interactions that are awkward today: comparing the capture box position against what's actually on the HUD, nudging mid-session when the player switches ships or when HUD scaling changes, and demonstrating to a new user how the tool works ("watch the box snap onto the deposit code as I move it").

## The control panel as home base

Even with edit mode, the control panel is not optional. It is the home base for:

- **Setup** — picking templates, choosing models, setting thresholds, entering a remote Ollama host. Things that aren't spatial and don't fit the overlay.
- **Inspection** — runtime status badges, alignment scores, last scan result. The "is everything OK?" surface.
- **Troubleshooting** — actionable status (red badges → click for remediation), curated event log (planned), raw log toggle for diagnostics.
- **Recovery** — when something fails, the user opens the control panel to figure out why and what to do.

The control panel is spawned at launch alongside the overlay. The user may minimize it. A planned tray icon allows re-summoning without returning to the launching console.

## Status badges as glanceable health indicators

The current status badges in the control panel are a deliberate design choice: color-coded, compact, glanceable. They beat a wall of text for "is everything OK?" at a glance.

The gap is not the badges themselves — it is that they are read-only when something is wrong. A red badge tells the user *that* something is wrong but not *what to do about it*.

The vision is: **same widget, two modes**.

- Green badge → passive indicator. No interaction needed.
- Red badge → also a CTA. Click or hover reveals the failure detail and one or more remediation actions ("Auto align failed for 30s — last score 0.34, threshold 0.50. [Pick template] [Adjust threshold] [Disable auto-align]").

This keeps the clean look in the happy path and only spends pixels on remediation when remediation is needed.

## Event log as a curated user surface

The console window shows raw loguru output. That is appropriate for the developer using the launching shell as a diagnostic surface, but it is the wrong surface for a player who just wants to know "did the scan work?"

The vision is a **curated event log** — a stream of semantic events ("Scanned ✓ TIN (Quantum)", "Auto-align lost lock — try Realign", "Ollama reconnected") that any UI can choose to render. The raw loguru log remains available behind a "Diagnostics" toggle in the control panel.

The curated stream is its own concern (`Event log`) with its own signal vocabulary, not a filtered view of loguru. This keeps the user-facing wording stable across log-format changes and lets the log be tested independently.

## Push-everything, with isolated polling

The architectural commitment is: **UIs subscribe to push signals; they do not poll**.

Some sources cannot push (Ollama health is the canonical example). For those, a single dedicated adapter polls the source and emits a signal on state change. The polling lives in one well-named place; UIs see only signals.

Two consequences worth naming:

- **Continuous scan is not polling**. It is a scheduler that publishes scan-trigger events at a configured interval. UIs see scan lifecycle signals; they don't time anything.
- **The web overlay should not poll either**. It should consume the same signals as the in-game overlay via Server-Sent Events (or equivalent). This is the EDA story applied end-to-end.

See the push-flow ADR for the formal rule and the SSE PRD for the web application.

## Coalesce at the edge

Push-everything is not "fire as fast as possible." High-frequency signals (scan results during a tight continuous loop, drag events during edit mode) should be **coalesced at the rendering edge**: latest value wins, drop intermediates, cap repaint at a humane rate (~10 Hz for visible UI). The bus carries truth; the renderer paces.

This belongs in the renderer, not in the publisher — publishers should not be in the business of guessing how often consumers want updates.

## Onboarding and first-run

A new user today opens the control panel and sees ~12 sliders, 4 spinboxes, and 14+ buttons. Auto-installing Ollama softens the dependency story but does nothing for the spatial configuration story.

The vision is a **3-step first-launch wizard**:

1. **Pick anchor** — show the available anchor templates with thumbnails; user picks one matching their HUD.
2. **Position capture** — overlay enters edit mode focused on the capture box; user drags it over the deposit code area; arrow keys for fine-tuning.
3. **Test scan** — user triggers a scan from the wizard; if a code is detected, the wizard confirms success and offers to save as a preset. If not, it offers troubleshooting paths (re-pick anchor, adjust offsets, swap Ollama model).

The wizard runs once on first launch and is available on demand thereafter from the control panel ("Re-run setup wizard"). The "heavier full-screen auto-detect scan" idea (auto-finding the deposit code area on screen) belongs *inside* this wizard as a nice-to-have, not as a runtime feature.

## Presets

Different ships, resolutions, and HUD scales require different capture and anchor settings. The current single global config does not serve a player with multiple ships.

The vision is **presets as a first-class concern**: save / load / delete named configurations, with a quick switcher accessible from the edit-mode toolbar in the overlay (so the player can swap ships and presets without leaving the game).

Presets are their own concern with their own actions and signals; they are *not* a wrinkle on top of Configuration. This keeps the Configuration vocabulary clean.

## Hotkey discovery and configuration

Hotkeys are central to the in-game flow. Today they are hard-coded (`7`, `Ctrl+7`, `8`) and discoverable only via a cheatsheet in the control panel — a panel the player cannot see while the game is fullscreen.

Two requirements:

- **Configurable** — users can rebind hotkeys from the control panel. Default bindings should be conservative (avoid common SC bindings).
- **Discoverable from the overlay** — the in-game overlay surfaces current hotkey bindings in edit mode (toolbar) and on first launch (transient hint).

## Failure-mode design

Most of the perceived "complexity" of the tool is not configuration — it is **what happens when things fail**. Auto-align loses lock. Ollama crashes. The OCR returns garbage. A new HUD update changes the deposit code rendering.

Each failure mode should have:

1. A **detection** path — the system observes the failure, ideally without polling.
2. A **signal** that describes the failure semantically.
3. A **status badge** that turns red.
4. A **remediation** that is one click away from the badge.
5. (Optional) A **curated event log entry** so the failure is visible in the log timeline.

Designing failure modes as first-class flows — not as edge cases tacked on after the happy path — is what separates "tool that works when everything is right" from "tool the user trusts."

## Edit mode and game input — the hard problem

Capturing mouse and keyboard reliably while a fullscreen game runs is finicky.

- **Borderless fullscreen** — works fine; standard input layering applies.
- **Exclusive fullscreen** — usually breaks; the game owns input.
- **Mode detection** — ORCA should detect SC's window mode at launch and warn if exclusive fullscreen is active ("Edit mode requires borderless windowed mode. Switch in SC settings.").

The vision does not promise edit mode in exclusive fullscreen. It promises a clear in-overlay message explaining what to change, and the slider fallback for users who can't or won't switch modes.

## What is intentionally not in the vision

To keep the vision sharp, these are explicit non-goals:

- **A unified "operator + player + companion" UI.** The roles are different; conflating them produces a UI that serves none of them well.
- **Server-side or multi-user state.** ORCA is a single-user tool. The web overlay is a second-screen view of the same local state, not a multi-tenant service.
- **Game automation or input synthesis.** ORCA reads the screen and shows results. It does not press buttons in the game.
- **Strict UI-to-UI parity.** Tablet UI may omit "Save Config." Web overlay may omit edit mode. Parity is per concern, declared in manifests, verified by tests.

## Open questions

- **Tray icon vs. menu bar app on Linux** — Windows tray is well-defined; Linux equivalents vary. Out of scope for the initial PRD; revisit when we ship to Linux users in volume.
- **Voice readout for the companion role** — interesting idea (the companion role is fundamentally about glanceability; voice removes the need to glance at all). Not committed.
- **Cross-game support** — ORCA is Star Citizen-specific. Anchor templates and HUD assumptions are deeply tied to SC. Cross-game is a different product.
