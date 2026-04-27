# PRD: GUI Duplication Refactor

## Purpose

Reduce code duplication between the generic GUI abstraction layer and the Tk-specific GUI implementation, improving maintainability and making future UI changes easier to implement.

## Problem Statement

The current codebase duplicates significant GUI state models, overlay state classes, overlay helper functions, and layout re-export logic across `src/scanning_tool/gui/` and `src/scanning_tool/gui/tk/`. This duplication creates multiple maintenance paths for the same behavior, increases the risk of drift, and makes it harder to extend or migrate the UI.

## Goals

- Consolidate shared GUI state and overlay state models into a single backend-agnostic layer.
- Preserve the Tk-specific implementation as a thin adapter with type narrowing only.
- Remove duplicate wrapper functions that re-export the same overlay behavior.
- Keep existing behavior intact while improving the architecture.

## Scope

### In scope

- Consolidating shared GUI state dataclasses and models.
- Refactoring overlay state accessors and wrapper APIs.
- Simplifying layout module re-exports.
- Leaving existing behavior nominally unchanged.

### Out of scope

- Rewriting the Tk UI rendering logic itself.
- Replacing the underlying overlay or capture behavior.
- Introducing new UI frameworks or migration targets.

## Duplication summary

### Shared GUI state duplication

Duplicated classes exist in:
- `src/scanning_tool/gui/state.py`
- `src/scanning_tool/gui/tk/control_state.py`

Duplicated models:
- `CaptureSliders`
- `AnchorSliders`
- `OverlaySliders`
- `SyncFlags`
- `ControlState`

### Overlay state duplication

Duplicated overlay state classes and accessors exist in:
- `src/scanning_tool/gui/overlay_state.py`
- `src/scanning_tool/gui/tk/overlay_state.py`

This includes:
- `CaptureOverlayState`
- `InfoOverlayState`
- `AnchorOverlayState`
- `OverlayState`
- `reset()` implementations
- property wrappers for capture, info, and anchor overlay state

### Overlay API wrapper duplication

Identical helper functions exist in:
- `src/scanning_tool/gui/overlays/__init__.py`
- `src/scanning_tool/gui/tk/overlays/__init__.py`

Duplicated functions:
- `show_overlay`
- `update_overlay_region`
- `destroy_all_overlays`

### Layout re-export duplication

Functionally identical helper modules:
- `src/scanning_tool/gui/layout.py`
- `src/scanning_tool/gui/tk/layout.py`

## Success criteria

- `gui/` contains a single shared definition for the common GUI state and overlay models.
- `gui/tk/` uses the shared definitions and adds only Tk-specific type annotations or behavior.
- The overlay API wrapper functions are not duplicated across `gui/overlays/__init__.py` and `gui/tk/overlays/__init__.py`.
- Existing overlay and UI behavior remains unchanged from the user perspective.
- New tests cover the shared model boundary and ensure no regression in overlay state handling.

## Implementation plan

1. Extract shared dataclass definitions into `src/scanning_tool/gui/state.py` and remove duplicates from `src/scanning_tool/gui/tk/control_state.py`.
2. Consolidate shared overlay state classes and property wrappers into `src/scanning_tool/gui/overlay_state.py`.
3. Refactor `src/scanning_tool/gui/tk/overlay_state.py` to import and extend shared state as needed, keeping only Tk-specific type details.
4. Remove duplicated wrapper functions from `src/scanning_tool/gui/overlays/__init__.py`; re-export the `tk` overlay implementation or directly delegate to it.
5. Consolidate layout re-export modules so `src/scanning_tool/gui/tk/layout.py` re-uses the shared `src/scanning_tool/gui/layout.py` definitions.
6. Add tests for the shared GUI state and overlay state boundaries, verifying both generic and Tk-specific consumers.
7. Update documentation or comments to describe the shared backend-agnostic GUI model and the thin Tk adapter role.

## Checklist

- [x] Confirm the shared models in `src/scanning_tool/gui/state.py` are complete and authoritative.
- [x] Refactor or remove duplicate models in `src/scanning_tool/gui/tk/control_state.py`.
- [ ] Consolidate overlay state classes in `src/scanning_tool/gui/overlay_state.py`.
- [x] Refactor `src/scanning_tool/gui/tk/overlay_state.py` to depend on shared overlay state.
- [x] Remove duplicated `show_overlay`, `update_overlay_region`, and `destroy_all_overlays` wrappers.
- [x] Simplify the layout module re-export pair.
- [ ] Add regression tests for overlay state and GUI state separation.
- [ ] Document the shared GUI model and adapter responsibilities.
- [ ] Validate existing behavior manually or via tests after refactor.
