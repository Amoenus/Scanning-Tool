# PRD: Pythonic Code Quality Improvements

## Purpose
Improve the `Scanning-Tool` codebase by aligning it with Pythonic best practices, reducing technical debt, and enabling cleaner static analysis and future refactors.

## Problem Statement
The current codebase contains a small set of Python style and architecture issues that reduce readability, increase maintenance effort, and prevent effective static type analysis. These issues include legacy import patterns, non-idiomatic file handling, unused imports, and package typing gaps.

## Goals
- Make the repository more idiomatic to modern Python standards.
- Eliminate known `ruff` lint issues and improve `mypy` compatibility.
- Reduce code complexity by replacing unnecessary patterns with Pythonic equivalents.
- Strengthen explicit domain modeling and package exports.
- Preserve existing behavior while improving maintainability.

## Proposed Improvements
1. Replace `from ... import *` star imports in compatibility wrappers with explicit exported names.
   - Primary target: `src/scanning_tool/domain/models.py`
   - Secondary target: `src/scanning_tool/gui/overlays/__init__.py`

2. Remove unused imports and clean up `__all__` exports.
   - `src/scanning_tool/__init__.py`
   - `src/scanning_tool/domain/ore_schemas.py`
   - `src/scanning_tool/gui/tk/overlays/__init__.py`

3. Prefer `pathlib.Path` and context managers for file I/O.
   - Use `with path.open(...)` instead of manual `open()` / `close()`.
   - Work with `Path` objects in helpers like `resource_path()` where possible.

4. Apply EAFP (easier to ask forgiveness than permission) to file loading.
   - Replace `path.exists()` pre-checks with `try/except FileNotFoundError` semantics.
   - Target file loader helpers such as `src/scanning_tool/deposits/scan_signatures.py`.

5. Use logging instead of `print()` for diagnostic and persistent messages.
   - Adopt consistent logging patterns in modules that already use `loguru` or `logging`.

6. Strengthen explicit type annotations and data modeling.
   - Encourage use of `dataclass` or typed domain objects for structured data.
   - Apply `str | None`, `Iterator[...]`, and `None` return types where appropriate.

7. Add package typing metadata for better `mypy` support.
   - Ensure the installed package includes `py.typed` where needed.
   - Resolve `import-untyped` diagnostics preventing full analysis.

8. Simplify helper code by using pure functions for stateless logic.
   - Consider replacing classes that merely wrap small helper functions with module-level helpers.
   - Keep stateful classes only where state is genuinely required.

9. Improve package compatibility shim behavior.
   - Reduce reliance on dynamic runtime import shims, favor explicit module exports.
   - Preserve compatibility only when necessary, with clear migration intent.

10. Align the runtime entrypoint with a clean `main()` pattern.
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
- `ruff check .` reports zero remaining issues for the targeted refactor area.
- `mypy .` no longer reports `import-untyped` for local package imports when typed metadata is available.
- The codebase uses explicit exports and avoids star imports in compatibility shims.
- File handling uses `pathlib.Path` and context managers consistently in the reviewed modules.
- No current behavior changes are introduced by the refactor.

## Risks
- Compatibility wrappers may break external import paths if exports are changed without preserving aliases.
- `mypy` gains may be limited until package typing metadata is fully adopted across dependencies.
- Over-refactoring could introduce unnecessary churn if applied too broadly.

## Next Steps
1. Implement explicit exports in `src/scanning_tool/domain/models.py` and `src/scanning_tool/gui/overlays/__init__.py`.
2. Remove the unused import warnings identified by `ruff`.
3. Refactor file loaders to use EAFP and `with Path.open`.
4. Add or confirm `py.typed` packaging support.
5. Re-run `ruff check .` and `mypy .` to validate the improvements.
