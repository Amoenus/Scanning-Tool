# PRD: System Tray Icon for Control Panel

## Purpose
Add a system tray icon so users who minimize the control panel can re-summon it without going back to the launching console window. Small UX polish that fits the launch-from-console operational model: the console is incidental to launch, and minimizing the control panel should not effectively hide the application.

## Problem Statement
ORCA is launched from a console (`launch_windows.bat` or shell script). This produces a console window, the control panel, and the in-game overlay. The user often minimizes the control panel during gameplay. Re-summoning it requires either alt-tabbing through windows (slow) or returning to the console (which is the wrong mental model — the console is for diagnostics).

A system tray icon is the standard Windows-native solution. Click to show/hide the control panel; right-click for a small menu (show / quit / re-run setup wizard). It is low-effort and high-value for the operator role.

## Goals
- Add a system tray icon visible while ORCA runs.
- Left-click toggles control-panel visibility (show if hidden, focus if visible, hide if focused).
- Right-click opens a context menu with: Show control panel, Re-run setup wizard, Quit.
- Tooltip on hover shows current scanner state ("Idle" / "Continuous scan active" / "Auto-align lost lock") sourced from Runtime status.
- Tray icon is optional — disabling it via config falls back to current behavior.

## Scope
### In scope
- Tray icon implementation on Windows (initial target).
- Show/hide/focus behavior for the control panel.
- Context menu with show / re-run wizard / quit actions.
- Tooltip wired to Runtime status read model.
- Config flag to disable tray icon.

### Out of scope
- Tray icon on Linux / macOS (defer until those platforms are supported in volume).
- Alternate icons reflecting state (single icon is enough; tooltip carries state).
- Notifications / balloon tips (would belong with the curated event log surface; out of scope here).

## Success Criteria
- ORCA runs with a tray icon visible by default on Windows.
- Left-click toggles control-panel visibility correctly across the show/focus/hide cycle.
- Quit from the tray menu performs a clean shutdown (services stop, signals deregister).
- Tooltip reflects current Runtime status without polling (subscribes to the relevant signals).
- The tray icon disappears on application exit.

## Quality Requirements
- Tray icon thread does not block the GUI main loop.
- Tooltip updates are throttled (~1 Hz max).
- Quit from the tray performs the same shutdown sequence as closing the control-panel window.
- Hidden control-panel state survives focus / show toggles cleanly.

## Operation Model
1. On launch, the bootstrap creates the tray icon if config allows.
2. Tray icon subscribes to Runtime status signals to update its tooltip.
3. User left-clicks: tray service publishes `RuntimeAction.ToggleControlPanel`.
4. The control-panel window's listener handles the action: shows if hidden, brings to front if visible-but-not-focused, hides if focused.
5. User right-clicks: context menu opens; selecting Quit publishes a clean shutdown action.

## Implementation Approach
- Use a Windows-native tray library (e.g. `pystray` or `infi.systray`).
- Run the tray loop on a daemon thread.
- Subscribe to Runtime status signals via the event bus abstraction.
- Add a `RuntimeAction.ToggleControlPanel` and a `RuntimeAction.QuitApplication` action.
- Provide an icon asset under `assets/`.

## Risks and Mitigations
- **Risk:** tray library has packaging issues with the current PyInstaller / launch script setup.
  - Mitigation: validate packaging in a small spike before broad rollout.
- **Risk:** users on Linux see a no-op or warning.
  - Mitigation: feature-detect and disable cleanly on unsupported platforms; warn once in the log.
- **Risk:** the tray icon outlives the application after a crash.
  - Mitigation: tray service registers with the bootstrap shutdown hook.

## Implementation Checklist
- [ ] Choose tray library and validate packaging.
- [ ] Add ORCA tray icon asset.
- [ ] Implement tray service with show/hide/focus toggle and quit menu.
- [ ] Add `RuntimeAction.ToggleControlPanel` and `RuntimeAction.QuitApplication`.
- [ ] Wire control-panel show/hide/focus listener.
- [ ] Wire tooltip to Runtime status signals.
- [ ] Add config flag to disable tray icon.
- [ ] Test clean shutdown via tray Quit.
- [ ] Document the tray behavior in `ux-vision.md`.
