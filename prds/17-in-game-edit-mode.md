# PRD: In-Game Edit Mode

## Purpose
Implement edit mode on the existing in-game overlays so spatial configuration (capture region, anchor region, info-label position) can be performed directly with mouse and keyboard while the game runs in fullscreen — replacing the alt-tab-to-sliders flow as the primary spatial-config interaction.

## Problem Statement
ORCA's spatial configuration today happens through twelve sliders in the Tk control panel. Each slider takes pixel coordinates with wide ranges; the cognitive mapping between "the box should be a bit to the left" and "decrement Capture Left from 1247 to 1217" is poor. More critically, this interaction requires alt-tabbing out of Star Citizen, which is friction-heavy in borderless fullscreen and breaks immersion in exclusive fullscreen.

The on-screen overlays already know where they are. The user can already see them. The natural input is to manipulate them directly. Decision `2026-04-29-in-game-edit-mode-as-primary-config-surface` commits to this direction; this PRD specifies the implementation.

## Goals
- Add a hotkey-toggled edit mode to the in-game overlays.
- Support mouse drag (move and resize) and arrow-key nudge for capture region, anchor region, and info-label position.
- Surface a small contextual toolbar at the active region's edge: dimensions readout, lock, reset, exit.
- Have all adjustments emit the same `ConfigAction` events that the Tk sliders publish, so existing slider sync works unchanged.
- Detect the game's window mode and surface a clear in-overlay message when edit mode is unavailable (exclusive fullscreen).
- Provide hotkey discovery from inside the overlay so the player does not need to alt-tab to the control panel cheatsheet.

## Scope
### In scope
- Edit mode state machine (idle → edit → idle), driven by `EditModeAction.EnterEditMode` / `ExitEditMode`.
- Selection, drag, resize, nudge, reset, and lock behaviors for capture region, anchor region, and info-label position.
- Contextual toolbar widget rendered at the active region.
- Hotkey toggle (default `F9`, configurable per PRD 24).
- Window-mode detection at launch with an in-overlay warning when exclusive fullscreen is active.
- Bidirectional sync with Tk control panel sliders via existing `config_changed` signal flow.
- Conformance scenarios for the Edit mode concern.

### Out of scope
- Editing non-spatial configuration (Ollama host, model, threshold, etc.) — those stay in the control panel.
- Preset switching from the toolbar (deferred to PRD 21; the toolbar leaves a slot for it).
- Any change to OCR or alignment behavior.
- Edit mode in exclusive fullscreen (we surface a message instead of attempting a workaround).

## Success Criteria
- Pressing the edit-mode hotkey from the game enters edit mode without alt-tabbing.
- A user can position the capture box over the deposit code area using only mouse and keyboard, without opening the control panel.
- Tk control panel sliders update live as overlays are dragged.
- Configuration values changed via edit mode are persisted via the existing `SaveConfig` action.
- In exclusive fullscreen, the in-overlay message clearly explains the limitation and how to switch to borderless windowed mode.
- The Edit mode conformance suite passes for every UI claiming the Edit mode concern.

## Quality Requirements
- Edit mode does not consume game input when inactive.
- Drag and nudge operations coalesce at the rendering edge (no flicker, ~10 Hz repaint cap).
- Edit mode actions emit `ConfigAction` events; they do not write to the Configuration read model directly.
- The toolbar has zero overlap with the rectangle being edited (positioned at the rectangle's edge with collision avoidance).
- Window-mode detection runs once at launch and on overlay re-show; it does not poll.

## Operation Model
1. User triggers edit-mode hotkey (default `F9`).
2. EditMode service publishes `EditModeAction.EnterEditMode`; in-game overlays update visual style (handles, dimensions); game input passthrough is disabled for the overlay scope.
3. User selects a region by clicking it (or via Tab cycling). Selected region's contextual toolbar appears at its edge.
4. User drags edges/corners to resize, drags interior to move, or uses arrow keys (1px) and Shift+arrow (10px) to nudge.
5. Each adjustment publishes `EditModeAction.DragRegion` / `NudgeRegion`, which translates into `ConfigAction.UpdateCaptureRegion` (or anchor/info equivalent). The Configuration concern updates `ConfigSnapshot`; downstream listeners (sliders, capture pipeline, web overlay) react via the standard signal flow.
6. User exits edit mode via toolbar button, hotkey, or Esc. Game input passthrough resumes.
7. User saves via existing `SaveConfig` action when satisfied.

## Implementation Approach
- Introduce an `EditModeService` inside the Edit mode concern. It owns `EditModeState` (active region, draft values, toolbar visibility) and publishes `edit_mode_changed` / `region_drafted` / `region_committed` signals.
- Use existing overlay rendering (`gui/tk/overlays/`) and add a toolkit-agnostic `EditModeRenderer` interface; the Tk implementation lives under `gui/tk/overlays/edit_mode.py`.
- Hook keyboard via the existing `keyboard` package (used by `services/hotkeys_service.py`); ensure mouse capture is restricted to the overlay window's bounds.
- Window-mode detection via Win32 APIs on Windows; Linux equivalent gated behind a feature flag.
- Reuse the `control_state.syncing.capture` / `syncing.anchor` flags to suppress slider feedback loops during drag.

## Risks and Mitigations
- **Risk:** input capture conflicts with the game (clicks reach the game while in edit mode).
  - Mitigation: ensure overlays are click-through when not in edit mode and click-opaque when in edit mode; document borderless-windowed requirement.
- **Risk:** edit-mode hotkey collides with game bindings.
  - Mitigation: default to `F9` (uncommon in SC); make configurable via PRD 24.
- **Risk:** rapid drag events overwhelm the renderer.
  - Mitigation: coalesce at the rendering edge per the push-flow ADR.
- **Risk:** users expect edit mode in exclusive fullscreen and assume it is broken.
  - Mitigation: explicit in-overlay message naming the requirement and the SC setting to change.

## Implementation Checklist
- [x] Define `EditModeAction` enum and signals (per PRD 16).
- [x] Define `EditModeState` read model.
- [x] Implement `EditModeService` and wire it into the bootstrap.
- [ ] Add overlay handles and dimension readout widgets for edit mode.
- [ ] Implement drag (move + resize) for capture region, anchor region, info-label position.
- [ ] Implement arrow-key nudge (1px) and Shift+arrow (10px).
- [ ] Implement Tab cycling between regions.
- [ ] Build the contextual toolbar widget (dimensions, lock, reset, exit, preset slot).
- [ ] Wire edit-mode hotkey toggle (default `F9`).
- [ ] Implement window-mode detection on Windows.
- [ ] Add in-overlay message for exclusive fullscreen / unsupported mode.
- [ ] Verify Tk slider sync updates live on overlay drag.
- [ ] Add Edit mode manifest entry to in-game overlay UI.
- [ ] Write conformance scenarios (enter/exit, drag, nudge, persist).
- [ ] Update `ux-vision.md` if implementation reveals refinements.
- [ ] Document edit-mode flow in `architecture/concerns-architecture.md`.
