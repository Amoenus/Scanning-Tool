# PRD: Pythonic Code Quality Improvements

## Purpose
Improve the `Scanning-Tool` codebase by aligning it with Pythonic best practices, reducing technical debt, and enabling cleaner static analysis and future refactors.

## Problem Statement
The current codebase is already largely modern, but it still contains a few Python style and architecture opportunities that reduce readability, increase maintenance effort, and prevent fully effective static type analysis. These issues include compatibility shim patterns, non-idiomatic file handling, logging inconsistencies, and package typing gaps.

## Goals
- Make the repository more idiomatic to modern Python standards.
- Eliminate known `ruff` lint issues and improve `mypy` compatibility.
- Reduce code complexity by replacing unnecessary patterns with Pythonic equivalents.
- Strengthen explicit domain modeling and package exports.
- Preserve existing behavior while improving maintainability.

## Findings
- The repo already uses `@dataclass`, `from __future__ import annotations`, and many typed APIs.
- Some modern Pythonic patterns are already in place, such as `pathlib.Path` in key I/O modules and typed `Optional` usages.
- `ruff` identified a few low-value issues that have already been addressed:
  - removed an unused `types` import in `src/scanning_tool/__init__.py`
  - removed an unused `JsonObject` import in `src/scanning_tool/domain/ore_schemas.py`
  - added `ControlState` to `__all__` in `src/scanning_tool/gui/tk/overlays/__init__.py`
- Remaining work is mostly about targeted modernization rather than large rewrites.

## Proposed Improvements
1. Replace compatibility shim star imports with explicit exported names.
   - Primary target: `src/scanning_tool/domain/models.py`
   - Keep `src/scanning_tool/gui/overlays/__init__.py` stable (already exported correctly).

2. Prefer `pathlib.Path` and context managers for file I/O where still legacy patterns exist.
   - Use `with path.open(...)` instead of manual `open()` / `close()`.
   - Work with `Path` objects in helpers like `resource_path()` where appropriate.

3. Apply EAFP (easier to ask forgiveness than permission) to file loading.
   - Replace `path.exists()` pre-checks with `try/except FileNotFoundError` semantics.
   - Target file loader helpers such as `src/scanning_tool/deposits/scan_signatures.py`.

4. Use logging instead of `print()` for diagnostic and persistent messages.
   - Adopt consistent logging patterns in modules that already use `loguru` or `logging`.

5. Strengthen explicit type annotations and data modeling.
   - Encourage use of `dataclass` or typed domain objects for structured data.
   - Apply `str | None`, `Iterator[...]`, and `None` return types where appropriate.

6. Add package typing metadata for better `mypy` support.
   - Ensure the installed package includes `py.typed` where needed.
   - Resolve `import-untyped` diagnostics preventing full analysis.

7. Simplify helper code by using pure functions for stateless logic.
   - Consider replacing classes that merely wrap small helper functions with module-level helpers.
   - Keep stateful classes only where state is genuinely required.

8. Reduce dynamic runtime import shim behavior where explicit exports are preferable.
   - Preserve compatibility only when necessary, with clear migration intent.

9. Align the runtime entrypoint with a clean `main()` pattern.
   - Ensure the application's launch path is explicit and testable.
   - Keep a single, modern module entrypoint pattern where possible.

## In Scope
- Refactoring code in the `src/scanning_tool` package to improve Python idioms.
- Addressing `ruff` lint issues and `mypy` import typing problems.
- Removing legacy patterns while keeping existing application behavior unchanged.

## Out of Scope
- Changing business logic or user-facing features.
- Rewriting large systems that are already well-structured and working.
- Upgrading or replacing major third-party dependencies unless required for the improvements.

## Success Criteria
- `ruff check src/scanning_tool` reports zero remaining issues in the targeted refactor area.
- `mypy .` no longer reports `import-untyped` for local package imports when typed metadata is available.
- The codebase uses explicit exports and avoids star imports in compatibility shims.
- File handling uses `pathlib.Path` and context managers consistently in the reviewed modules.
- No current behavior changes are introduced by the refactor.

## Risks
- Compatibility wrappers may break external import paths if exports are changed without preserving aliases.
- `mypy` gains may be limited until package typing metadata is fully adopted across dependencies.
- Over-refactoring could introduce unnecessary churn if applied too broadly.

## Next Steps
1. Implement explicit exports in `src/scanning_tool/domain/models.py`.
2. Refactor file loaders to use EAFP and `with Path.open`.
3. Add or confirm `py.typed` packaging support.
4. Standardize logging instead of `print()` in modules that emit diagnostic messages.
5. Re-run `ruff check src/scanning_tool` and `mypy .` to validate the improvements.
