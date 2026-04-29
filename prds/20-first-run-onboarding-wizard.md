# PRD: First-Run Onboarding Wizard

## Purpose
Introduce a 3-step first-launch wizard that walks a new user through anchor selection, capture-region positioning, and a test scan. The wizard replaces the slider-wall onramp for new users without removing the manual path for power users.

## Problem Statement
A new user opening ORCA today sees roughly twelve sliders, four spinboxes, and fourteen buttons in a single panel. Auto-installing Ollama removes the dependency-setup friction but does nothing for the spatial-configuration friction. There is no guided flow from "I just installed ORCA" to "I just scanned my first deposit."

The combination of in-game edit mode (PRD 17) and the per-concern architecture (PRD 16) makes a clean wizard implementable: edit mode handles the spatial configuration interactively, the wizard sequences the steps, and each step publishes existing concern actions.

## Goals
- Run a 3-step wizard on first launch (no `config.json` present, or a flag indicating first run).
- Step 1: Pick an anchor template from `assets/anchor_templates/` with thumbnail previews.
- Step 2: Use in-game edit mode to position the capture box over the deposit-code area.
- Step 3: Trigger a test scan; on success, offer to save as a preset (when PRD 21 is implemented) or save to default config; on failure, offer guided troubleshooting.
- Make the wizard re-runnable on demand from the control panel ("Re-run setup wizard").
- Keep the manual path (existing slider-based config) intact for power users.

## Scope
### In scope
- Wizard UI in the control panel (dedicated `Toplevel` window with step navigation).
- First-launch detection (e.g. absence of a `setup_complete` flag in `config.json`).
- Anchor template gallery with thumbnails.
- Hand-off to in-game edit mode for step 2 (the wizard window minimizes; the overlay handles drag/nudge; the wizard re-foregrounds on confirmation).
- Test-scan integration that reports success/failure with a clear next-step prompt.
- "Re-run setup wizard" action in the control panel.

### Out of scope
- A "heavier full-screen auto-detect scan" that locates the deposit-code area automatically (interesting future work; not committed in this PRD).
- Editing every advanced setting from the wizard (it covers spatial setup only; advanced settings remain in the control panel).
- Multi-language localization.

## Success Criteria
- A new user who launches ORCA for the first time goes through the wizard without consulting documentation.
- The wizard completes in under five minutes for a typical user.
- After completing the wizard, the user can perform a successful scan in-game.
- The wizard is re-runnable from the control panel and produces the same result as on first launch.
- The wizard publishes only standard concern actions (no special wizard-only configuration paths).

## Quality Requirements
- Each step is self-contained: the user can back up to the previous step without losing state.
- Step 2 hands off to edit mode and re-foregrounds gracefully.
- The wizard does not block the rest of the application; the user can dismiss it and return later.
- All wizard text is plain language (no log-level jargon, no module names).

## Operation Model
1. On launch, bootstrap checks for a `setup_complete` marker. If absent, the wizard is queued to open after the control panel and overlay are visible.
2. Step 1 — Anchor pick: gallery of templates from `assets/anchor_templates/` with thumbnails. User picks one. Wizard publishes `ConfigAction.UpdateAnchorTemplate` (new action introduced by this PRD).
3. Step 2 — Position capture: wizard explains the goal, then publishes `EditModeAction.EnterEditMode` focused on the capture region. The wizard window minimizes; the user drags the capture box over the deposit-code area; pressing Enter (or clicking "Done" in the edit-mode toolbar) returns to the wizard.
4. Step 3 — Test scan: wizard publishes `ScanAction.SingleScan`. On `scan_completed` with a recognized code, the wizard shows success and offers "Save preset" (per PRD 21) or "Save config." On `scan_failed` or unrecognized code, the wizard shows troubleshooting options (re-pick anchor, re-position capture, swap Ollama model).
5. On completion, wizard sets the `setup_complete` flag via `ConfigAction.SaveConfig`.

## Implementation Approach
- Build the wizard as a `Toplevel`-based UI that consumes the same concern actions as the rest of the application.
- The anchor picker reuses existing `assets/anchor_templates/` discovery logic; thumbnail rendering can use PIL.
- Step 2's edit-mode hand-off reuses the EditMode service from PRD 17.
- The test-scan step subscribes to `scan_completed` / `scan_failed` for the duration of the step.
- Re-run is a `RuntimeAction.RunSetupWizard` (or similar) wired to the wizard's launch entry point.

## Risks and Mitigations
- **Risk:** the wizard depends on PRD 17 (edit mode) being implemented.
  - Mitigation: order PRDs accordingly; ship PRD 17 first.
- **Risk:** test scan fails for reasons unrelated to setup (Ollama not started yet on first run).
  - Mitigation: gate the test-scan step on `ollama_readiness_changed` ready=true; display a "Waiting for Ollama" sub-state.
- **Risk:** users who upgrade do not see the wizard but want to use it.
  - Mitigation: the "Re-run setup wizard" action is always available in the control panel.

## Implementation Checklist
- [ ] Define `setup_complete` flag in config.
- [ ] Build wizard `Toplevel` with step navigation framework.
- [ ] Implement step 1 (anchor picker with thumbnails).
- [ ] Add `ConfigAction.UpdateAnchorTemplate` (selects which template to use).
- [ ] Implement step 2 (hand-off to edit mode, re-foreground on confirm).
- [ ] Implement step 3 (test scan with success / failure paths).
- [ ] Add troubleshooting prompts for step-3 failures.
- [ ] Wire `setup_complete` flag write on wizard completion.
- [ ] Add "Re-run setup wizard" action to the control panel.
- [ ] Mirror in Qt control panel.
- [ ] Conformance scenarios for each step (anchor pick, edit-mode hand-off, test scan).
- [ ] Update `ux-vision.md` once shipped.
