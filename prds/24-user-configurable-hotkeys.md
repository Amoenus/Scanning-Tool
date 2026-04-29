# PRD: User-Configurable Hotkeys with In-Overlay Discovery

## Purpose
Make ORCA's hotkeys user-configurable from the control panel and surface current bindings inside the in-game overlay so the player does not need to alt-tab to a cheatsheet that lives behind the game window.

## Problem Statement
Today's hotkeys (`7`, `Ctrl+7`, `8`) are hard-coded in `services/hotkeys_service.py` and documented only in the Runtime Status section of the Tk control panel. Two problems follow:

- **Collisions with Star Citizen bindings** are unavoidable for some users; with hard-coded hotkeys there is no escape hatch except to rebind in SC.
- **Discoverability is broken in the in-game flow** — the player cannot see the cheatsheet because the control panel is not the active window. The vision (UX vision doc, edit-mode ADR) puts the in-game overlay at the center of the player flow, so hotkey discovery must move there too.

PRD 17 (edit mode) introduces a new hotkey (`F9`); PRD 21 (presets) introduces preset cycling; further PRDs may add more. Without a configurable, discoverable hotkey system, the bindings sprawl becomes its own problem.

## Goals
- Centralize hotkey definitions in a single registry covering current bindings (single scan, continuous toggle, capture-box toggle) and future bindings (edit mode, preset cycle).
- Allow users to rebind every hotkey from the control panel.
- Surface current bindings in the in-game overlay in two places: a transient first-launch hint and the edit-mode toolbar.
- Detect collisions (two actions bound to the same key) and warn at bind time.
- Persist bindings in `config.json`.

## Scope
### In scope
- Hotkey registry with per-action default bindings.
- Control-panel section for viewing and rebinding hotkeys.
- A capture flow: user clicks "rebind" next to an action, presses the desired key combination, registry updates.
- Persistence in `config.json` under a `hotkeys` key.
- Conflict detection at bind time.
- In-overlay discovery: transient hint on first launch, persistent display in edit-mode toolbar.

### Out of scope
- Per-preset hotkey overrides.
- Multi-step / chord shortcuts beyond simple modifier+key combinations.
- OS-level hotkey precedence handling beyond what the existing `keyboard` library provides.
- Localized key naming (use the `keyboard` library's canonical names).

## Success Criteria
- A user can rebind any hotkey from the control panel and have it take effect immediately (no restart).
- Conflicts (two actions bound to the same key) are detected and surfaced at bind time.
- The in-game overlay shows current bindings in the edit-mode toolbar.
- A first-launch hint (transient) shows the most important bindings briefly when the overlay first appears.
- Persisted bindings survive restart and config reload.
- Hotkey conformance scenarios verify rebinding, persistence, and conflict detection.

## Quality Requirements
- Hotkey registry is the single source of truth — services do not subscribe to `keyboard` directly.
- Default bindings are conservative and documented in the registry definition.
- Rebinding takes effect through the existing event bus; no service restart required.
- Hotkey labels in the UI use the `keyboard` library's canonical key names (no toolkit-specific naming).

## Operation Model
1. On launch, the hotkey service loads bindings from config (or defaults if absent) and registers them with the `keyboard` library.
2. Each registered hotkey publishes a corresponding action (`ScanAction.SingleScan`, `EditModeAction.EnterEditMode`, etc.).
3. User opens the control panel's Hotkeys section, sees current bindings, clicks "rebind" next to an action.
4. The UI captures the next key combination and publishes `RuntimeAction.RebindHotkey(action=..., key=...)`.
5. The hotkey service unregisters the old binding, registers the new one, and publishes `hotkey_rebound`. The registry persists via `ConfigAction.SaveConfig`.
6. The in-game overlay's edit-mode toolbar listens for `hotkey_rebound` and updates its displayed bindings.

## Implementation Approach
- Define a `HotkeyRegistry` containing `(action_name, default_key)` entries.
- Refactor `services/hotkeys_service.py` to read from the registry instead of hard-coding bindings.
- Add a `HotkeysSection` to the control panel.
- Surface current bindings in the edit-mode toolbar (depends on PRD 17).
- Add a transient first-launch hint via the in-game overlay (renders for ~5 seconds then fades).

## Risks and Mitigations
- **Risk:** users bind a key that is already used by Star Citizen, causing the game to react too.
  - Mitigation: warn at bind time if the key is in a known SC default set; users can ignore the warning.
- **Risk:** the `keyboard` library's hot-rebinding is racy.
  - Mitigation: serialize register/unregister calls through the hotkey service; test under rapid rebind.
- **Risk:** conflict-detection becomes user-hostile if it blocks valid rebinds.
  - Mitigation: warn but allow override; user can confirm to proceed.

## Implementation Checklist
- [ ] Define `HotkeyRegistry` with default bindings.
- [ ] Refactor `services/hotkeys_service.py` to consume the registry.
- [ ] Add `RuntimeAction.RebindHotkey` and `hotkey_rebound` signal.
- [ ] Add `HotkeysSection` to the Tk control panel.
- [ ] Mirror in Qt control panel.
- [ ] Add `hotkeys` field to `config.json` schema with persistence.
- [ ] Implement conflict detection and bind-time warning.
- [ ] Surface current bindings in the edit-mode toolbar (depends on PRD 17).
- [ ] Add transient first-launch hint to the in-game overlay.
- [ ] Conformance scenarios for rebind, persistence, and conflict detection.
- [ ] Update `ux-vision.md` once shipped.
