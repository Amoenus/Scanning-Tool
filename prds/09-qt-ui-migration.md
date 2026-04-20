# PRD: PyQt6 Configuration UI Migration

## Purpose

Replace the existing Tkinter-based native configuration UI with a modular PyQt6-based control panel. This migration enables a cleaner, more maintainable GUI architecture and provides the first step toward a fully native Qt replacement of the Scanning Tool control experience.

## Problem Statement

The current scanning tool GUI is implemented in Tkinter, which limits visual fidelity, modularity, and long-term maintainability. The codebase also mixes UI-specific widgets with runtime state handling, making it harder to migrate incrementally and to keep GUI components modular.

As the project moves toward a full PyQt6 migration, there is no formally defined PRD for how the new UI should be structured, how sections should be ported, or what success looks like.

## Goals

- Introduce a modular PyQt6 UI layer for the configuration/control panel.
- Preserve existing runtime state, configuration models, and overlay behavior during the migration.
- Provide a reusable Qt `SliderControl` component with slider + manual numeric entry behavior.
- Keep GUI components loosely coupled through a shared Qt section context and section interface.
- Allow the migration to proceed incrementally, with Tkinter remaining available as a fallback until Qt is stable.

## Scope

### In scope

- Add PyQt6 as a required dependency for the application.
- Create a Qt application launcher module and a shared Qt widget module.
- Define a Qt section interface and implement the first modular Qt sections.
- Port key configuration sections incrementally while preserving config state binding.
- Maintain the existing Flask browser overlay as a separate renderer.

### Out of scope

- Rewriting the browser overlay or web API.
- Replacing the overlay rendering pipeline itself.
- Implementing the full Qt version of every section in a single pass.
- Removing Tkinter until the Qt path is verified stable.

## Success Criteria

- The application can launch the new Qt control panel when configured to do so.
- The new Qt launcher and widget modules compile and start without syntax errors.
- The Qt slider control supports both drag and manual numeric entry.
- The new UI architecture is modular: sections are independently defined and wired through a shared Qt section context.
- The existing Tkinter path remains available and runs as a fallback when PyQt6 is unavailable.
- The migration path is documented and ready for further section-by-section porting.

## Quality Requirements

- Qt GUI components must be reusable and independent of one another.
- The Qt section model must avoid embedding Tkinter-specific types.
- Style and theming should be centralized and easy to extend.
- The launcher should choose UI backend via configuration or environment variable.
- Changes should be low-risk and not disrupt current scan or overlay functionality.

## Operation Model

1. `main.py` loads configuration and runtime state as before.
2. The selected GUI backend is determined from config or environment.
3. If `qt` is selected and PyQt6 is installed, the Qt launcher starts.
4. The Qt launcher builds a scrollable main window and instantiates configured Qt sections.
5. Each Qt section receives the shared context and creates its own controls/widgets.
6. Existing capture and overlay state remain the canonical source of truth.

## Implementation Approach

- Add `pyqt6` to the main dependencies.
- Create a `src/scanning_tool/gui/qt_widgets.py` module with reusable Qt widgets like `SliderControl`.
- Create a `src/scanning_tool/gui/qt_app.py` launcher capable of booting the Qt UI.
- Add a modular `src/scanning_tool/gui/qt_sections/` package with a shared `QtSectionContext` and individual section implementations.
- Wire `main.py` to respect `gui_backend` configuration and fall back to Tkinter when `qt` is unavailable.
- Port one configuration section first (e.g. capture region) before porting additional sections.
- Keep the existing Tkinter `src/scanning_tool/gui/` package intact until the Qt path is fully validated.

## Risks and Mitigations

- Risk: PyQt6 import fails in some environments.
  - Mitigation: keep Tkinter fallback logic and clear warning logs.
- Risk: inconsistent runtime state binding between Qt and existing services.
  - Mitigation: reuse the same `ConfigData`, `ScanState`, and `ServiceState` objects with a shared context.
- Risk: migration scope grows too large.
  - Mitigation: port sections incrementally and preserve the current app behavior at each step.
- Risk: increased packaging complexity due to PyQt6.
  - Mitigation: add it to main dependencies intentionally and validate packaging.

## Notes

- This PRD is the first migration milestone; further PRDs may cover full Qt section coverage, UX polish, and eventual Tkinter removal.
- A separate PRD should later define the final deprecation of Tkinter once Qt proves stable.
