# Decision: In-game edit mode as primary spatial config surface

## Status
Accepted

## Context

Spatial configuration in ORCA today happens through sliders in the Tk control panel: four sliders for the capture region, four for the anchor region, two for anchor offset, two for result-display offset. Each slider has a wide pixel-coordinate range (e.g. 0–3000). A new user opens the panel and sees twelve sliders with no obvious mapping to the on-screen rectangles they control.

This is a usability problem at setup time, but the deeper problem is *runtime*. Star Citizen runs fullscreen. Adjusting a slider while in-game requires alt-tabbing — friction-heavy in borderless fullscreen, broken in exclusive fullscreen. Yet the user inevitably wants to nudge the capture box mid-session: ship change, HUD scale change, drift after a long flight, or a freshly-installed game patch that moved a HUD element.

The on-screen overlays already know where they are. The user can already see them. The natural input is to drag and nudge them directly — not to translate "the box is too far left" into "decrement the Capture Left slider by 30."

## Decision

Spatial configuration becomes primarily mouse-driven through an **in-game edit mode** on the existing overlays. The desktop sliders remain as a power-user fallback and exact-value input.

Edit mode behavior:

- A configurable hotkey (default `F9`) toggles edit mode.
- Overlay rectangles become visually distinct (handles, dimension readout) and accept input. Game input is suppressed for the overlay's input scope.
- Mouse drags resize and reposition rectangles. Arrow keys nudge by 1px. Shift+arrow nudges by 10px. Tab cycles between rectangles.
- A small contextual toolbar appears at the edge of the active rectangle: dimensions readout, lock, reset, exit edit mode, and (when implemented) preset switcher.
- All adjustments emit the same `ConfigAction` events the desktop sliders publish. Sliders update via the same signals they already subscribe to.
- Exit returns input to the game.

The full design is captured in PRD 17 (in-game edit mode).

This decision implies the **control panel is the home base, not the primary configuration tool**. It hosts setup that is non-spatial (templates, models, hosts), inspection (status badges, event log), and troubleshooting. The spatial setup that dominates current first-use friction is moved to the overlay.

## Consequences

- **The slider wall stops being the new-user onramp.** New users go through the first-run wizard (PRD 20) which uses edit mode internally; sliders become an advanced fallback.
- **Mid-session reconfiguration is no longer painful.** A player can nudge the capture box without alt-tabbing.
- **Edit mode crosses concerns** — it publishes `ConfigAction` events. The concerns architecture allows this; edit mode is allowed to use Configuration's actions but not write to Configuration's read model directly.
- **Input capture in fullscreen is finicky.** Borderless fullscreen works; exclusive fullscreen does not. ORCA detects window mode and surfaces an in-overlay message when edit mode is unavailable. We do not promise edit mode in exclusive fullscreen.
- **The desktop control panel becomes simpler in role** — diagnostic and inspection-first. This is a positive but requires the actionable-status-badges work (PRD 18) and the curated event log (PRD 19) to fully land.
- **Hotkey discovery moves to the overlay.** Edit mode toolbar surfaces current bindings; first launch shows a transient hint. The control panel is no longer the only hotkey surface.
