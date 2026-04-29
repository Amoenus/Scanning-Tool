# PRD: Configuration Presets

## Purpose
Add multi-preset support so a user can save, load, and switch between named configurations (per ship, per resolution, per HUD scale). Expose a quick switcher from the in-game edit-mode toolbar so a player changing ships does not need to leave the game to swap settings.

## Problem Statement
ORCA today has one global configuration. A player with multiple ships, or who plays at multiple resolutions, has no way to keep distinct capture-region and anchor settings for each. They either re-tune sliders every time they switch context, or they tune for the most common case and accept misalignment for the others.

The per-concern architecture (PRD 16) makes presets implementable as their own concern with their own actions, signals, and read model. This keeps the Configuration concern's vocabulary clean (no "preset" wrinkle on top of every config action).

## Goals
- Define a Presets concern with its own action and signal namespace.
- Support save / load / delete / rename of named presets.
- Persist presets in the existing config storage (a `presets` field in `config.json`).
- Surface preset switching from two places: the control panel (full management UI) and the in-game edit-mode toolbar (quick switcher).
- Keep the current "global" config working as the default unnamed preset for users who don't engage with presets.

## Scope
### In scope
- `PresetAction` enum: `SavePreset`, `LoadPreset`, `DeletePreset`, `RenamePreset`, `ApplyCurrentAsPreset`.
- `preset_changed`, `preset_persisted`, `preset_load_failed` signals.
- `PresetList` and `Preset` read models.
- Storage in `config.json` under a `presets` key; one preset is marked `active`.
- Control-panel UI for full preset management (list, save current, load, delete, rename).
- Quick-switcher widget in the edit-mode toolbar (dropdown or cycle hotkey).
- Conformance scenarios for the Presets concern.

### Out of scope
- Sharing presets between users (export/import is a future PRD).
- Per-preset hotkey overrides (covered separately in PRD 24 if scoped).
- Auto-detecting which preset to apply based on game state.

## Success Criteria
- A user can save the current configuration as a named preset from the control panel.
- A user can switch presets from the in-game edit-mode toolbar without alt-tabbing.
- Switching presets immediately updates capture region, anchor region, anchor template, offsets, and result-display offset.
- Presets persist across application restarts.
- The Tk and Qt control panels render identical preset state.
- Conformance scenarios verify save/load/delete/rename and the active-preset marker.

## Quality Requirements
- Preset operations are atomic: a partial-load (some fields applied, others not) is not a valid state.
- The active preset is the source of truth — `ConfigSnapshot` reflects the active preset's values.
- Renaming a preset preserves its `active` status.
- Preset names are validated (non-empty, unique, max length).

## Operation Model
1. User saves current configuration as a preset via control panel: `PresetAction.SavePreset(name=...)`.
2. The Presets service captures the current `ConfigSnapshot`, stores it under the given name, and publishes `preset_persisted`.
3. User loads a preset via control panel or edit-mode toolbar: `PresetAction.LoadPreset(name=...)`.
4. The Presets service marks the preset as active, writes its values into the live config, and publishes `preset_changed` followed by `config_changed` for each affected field.
5. UIs subscribed to Configuration update accordingly (sliders, overlays, capture pipeline).

## Implementation Approach
- Define the Presets concern's vocabulary per PRD 16.
- Implement `PresetService` that owns the preset list and applies preset values via the existing Configuration actions (no direct config writes — preserves the cross-concern rule).
- Add a `PresetsSection` to the control panel.
- Add a quick switcher to the edit-mode toolbar (PRD 17 leaves a slot for it).
- Bind a cycle hotkey (Ctrl+`[` / Ctrl+`]`) for rapid switching, configurable per PRD 24.

## Risks and Mitigations
- **Risk:** preset format drifts from on-disk schema across releases.
  - Mitigation: include a `preset_schema_version`; provide a one-time migration for older formats.
- **Risk:** users accidentally overwrite a preset.
  - Mitigation: "Save preset" with an existing name shows a confirmation; "Save as" creates new.
- **Risk:** preset switching mid-scan produces inconsistent state.
  - Mitigation: preset switch is atomic and only takes effect between scan cycles; document the behavior.

## Implementation Checklist
- [ ] Define `PresetAction`, signals, and read models per PRD 16.
- [ ] Implement `PresetService` with save/load/delete/rename.
- [ ] Add `presets` and `active_preset` fields to `config.json` schema.
- [ ] Build `PresetsSection` in the control panel.
- [ ] Mirror in Qt control panel.
- [ ] Add quick switcher to the edit-mode toolbar (depends on PRD 17).
- [ ] Add cycle hotkey wiring (depends on PRD 24).
- [ ] Validate preset names (non-empty, unique, length cap).
- [ ] Write conformance scenarios (save, load, delete, rename, active).
- [ ] Document the Presets concern in `architecture/concerns-architecture.md`.
