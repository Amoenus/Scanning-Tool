# PRD: Folder Restructure and Logical Separation

## Purpose
This PRD defines the required repository restructure to bring the scanning tool into alignment with best practices for package separation, maintainability, and clear architectural boundaries.

## Problem Statement
The current repository contains a mix of scripts, domain logic, configuration loading, and runtime orchestration that is not consistently organized by responsibility. This makes it harder to maintain, harder to test, and increases the risk of import cycles or broad mutable state.

## Goals
- Restructure the repository into clear, responsibility-based packages.
- Separate configuration models from runtime domain models and state.
- Keep low-level utilities and core primitives isolated from higher-level services.
- Make entrypoints simple and focused on dependency composition.
- Support future refactors without changing core scanner behavior.

## Scope
### In scope
- Defining a target package layout for the scanning tool.
- Reorganizing modules so that each package owns one concern.
- Moving configuration types into a dedicated `config/` package.
- Separating domain models into `domain/` and `deposits/` packages.
- Consolidating runtime components into `services/` and `state/` packages.
- Moving capture, alignment, and OCR orchestration into `core/` and `services/` packages.
- Placing GUI and overlay responsibilities into `gui/` and `web/` packages.

### Out of scope
- Changing the scanner's business rules or user-facing behavior.
- Introducing new features beyond the folder restructure.
- Rewriting the OCR or anchor alignment algorithms.

## Success Criteria
- The codebase has a clearly defined package layout that matches documented architecture.
- Domain models are separated from configuration models and runtime state.
- Entrypoint modules only compose dependencies and start services.
- The new folder structure supports local editable install and package imports.
- Existing tests continue to pass after the restructure.

## Required Folder Structure
The repository should adopt a structure similar to this:

- `src/`
  - `config/`
  - `domain/`
  - `deposits/`
  - `services/`
  - `state/`
  - `core/`
  - `gui/`
  - `ollama/`
  - `web/`
  - `__init__.py`

The existing top-level scripts should remain entrypoints only, with core logic migrated into the package structure.

## Quality Requirements
- Use explicit domain types (`dataclass`, `TypedDict`, `BaseModel`) rather than raw dictionaries.
- Avoid global mutable state and compatibility shims as long-term architecture.
- Keep package boundaries narrow and imports acyclic.
- Ensure `config` is static after load and runtime state is owned by the pipeline that uses it.
- Keep the package layout consistent with the repository's architecture docs and coding standards.

## Operational Impact
- Developers should be able to locate configuration, state, and domain code by package name.
- Future extensions like remote OCR providers, web overlay improvements, or enhanced capture regions should be easier to add without broad refactors.
- This restructure enables stronger test isolation and clearer runtime wiring.
