# Scanning Tool Coding Standards

This document defines coding conventions for the Scanning Tool repository. It is intended to keep the codebase consistent, maintainable, testable, and aligned with strong typing and SOLID principles.

## 1. Naming

- Use descriptive, intention-revealing names for variables, functions, classes, and modules.
- Prefer nouns for classes and dataclasses, verbs for functions and methods.
- Avoid abbreviations unless they are well-known domain terms.
- Use `snake_case` for functions, methods, variables, and module names.
- Use `PascalCase` for classes, dataclasses, and exception types.
- Use `UPPER_SNAKE_CASE` for constants, and define constants at the top of the file or in a central module when shared across the project.
- Use a single leading underscore (`_name`) for internal/protected members and a double leading underscore (`__name`) only when class-private name mangling is intentionally required.
- Use `__all__` for public API exports in modules that intentionally re-export names.
- Prefer specific domain terms over generic names like `manager`, `handler`, or `helper`.
- Keep public API names stable and avoid renaming without a clear migration path.

Example:
- `capture_service`, not `cs`
- `ScanResultFactory`, not `ResultMaker`
- `capture_region`, not `cap_reg`
- `AnchorRegionTracker`, not `AnchorManager`

## 2. Types and typing

- Prefer narrow, explicit types over broad types.
- Avoid `Any` unless there is no practical alternative.
- Use `TypedDict`, `dataclass`, and `BaseModel` for structured data shapes.
- Use `Optional[T]` only when the value may legitimately be absent, not as a generic nullable marker.
- Use `Union` sparingly and only for values that can legitimately be multiple types.
- Use `Mapping`, `Sequence`, `Iterable`, and `Collection` for generic inputs instead of concrete container types when possible.
- Prefer concrete fixed-shape types like `tuple[int, int, int, int]` for coordinate or region values.
- Validate external or untrusted input at the boundary and immediately convert it into strongly typed domain objects.
- Prefer immutable types for value objects and configuration data when mutation is not required.
- Keep return types explicit and avoid returning raw `dict`, `list`, or `tuple` where a domain model improves clarity.

Example:
- `def capture(self, region: CaptureRegion) -> Image.Image:`
- `def to_scan_signature(self) -> Optional[ScanSignature]:`
- `def load_from_csv(cls, path: Path) -> "SignatureRegistry":`

## 3. Small, focused methods

- Keep methods short, focused, and easy to reason about.
- A method should do one thing and do it well.
- Extract small private helpers for distinct transformation, validation, or side-effect steps.
- Avoid deeply nested conditionals and long try/except blocks.
- Favor clear control flow over clever one-liners.
- Use helper method names to express intent rather than comments.
- Prefer composition of small methods over large, monolithic functions.
- Aim for methods that are easy to unit test in isolation.

Example:
- Extract `_run_ocr_pipeline`, `_capture_screen_region`, and `_align_before_capture` instead of one large `_do_capture` method.

## 4. Architecture and SOLID principles

### Single Responsibility Principle
- Each class, module, and package should have one reason to change.
- `config_service` should manage configuration only.
- `capture_service` should own capture and OCR flow only.
- `domain.models` should define business types only.
- `gui` modules should render UI and delegate behavior to services.

### Open/Closed Principle
- Prefer extensibility through composition and abstraction rather than modifying existing code.
- Add new capabilities by extending behavior with new classes or services, not by changing core business logic.

### Liskov Substitution Principle
- Design abstractions so derived types can be used anywhere the base type is expected.
- Keep protocols and service interfaces stable and compatible with implementers.

### Interface Segregation Principle
- Avoid large interfaces with many unrelated methods.
- Define small, focused protocols or service interfaces for each role.

### Dependency Inversion Principle
- Depend on abstractions, not concrete implementations.
- Pass dependencies through constructors or factories instead of importing globals.
- Keep dependencies explicit in class signatures and entrypoint wiring.
- Assemble concrete adapters, services, and handler wiring once in the bootstrap/composition root, and override them with fakes or no-op adapters during tests.

### Event-driven and command/query separation
- Prefer explicit command and event message types for app entrypoints and internal workflows.
- Keep commands as single-responsibility mutation requests and events as facts that trigger side effects or view updates.
- Use small immutable data structures for messages and avoid embedding business logic in event payloads.
- Wire command handlers, event handlers, and infrastructure adapters in one central bootstrap location, not through hidden global imports.
- Treat side effects and read-model updates as event listeners, not part of core business logic.
- Use `blinker` as the repository’s in-process event bus implementation for internal application signaling and handler dispatch.

## 5. Package and module structure

- Keep package boundaries clear: `config`, `domain`, `deposits`, `services`, `state`, `gui`, `core`, `ollama`, and `web`.
- Use a proper Python package layout with `pyproject.toml` and a top-level package module.
- Support a local editable install (`pip install -e .`) for developer workflows when feasible.
- Structure code into separable components and avoid a flat script-style repository layout.
- Prefer a small reusable core package with isolated dependencies, and extend via higher-level packages or submodules.
- Only export necessary symbols from package `__init__.py` files.
- Avoid cross-package import cycles.
- Put low-level helpers and reusable primitives in `core/`.
- Keep domain models separate from runtime state and configuration models.
- Organize code by responsibility, not by file size.
- Keep testables separate from UI and runtime orchestration.
- Prefer packages over single file utility modules. If a file name ends with `_utils.py`, it is usually hiding a structural problem.
- Use a predictable package layout with `src/project_name/...`, a separate `tests/` folder, and explicit configuration files. This makes imports predictable and onboarding easier.

### Application entrypoint
- Keep `main.py` boring: it should orchestrate setup, build the application from components, and start the runtime.
- Avoid putting business logic, setup conditionals, or environment-specific decisions in the entrypoint.
- Use `main.py` as a conductor, not as the place where the actual work happens.

## 6. State management

- Treat configuration as static after loading.
- Avoid broad module-level mutable state and compatibility shims except as a short-lived migration bridge in this single-user application.
- Prefer explicit application context or service object state passed through constructors.
- Keep runtime state local to the pipeline, GUI, or service that owns it.
- Use `frozen=True` dataclasses for immutable value objects and config if possible.
- If global state is unavoidable, document its purpose and limit its surface area.

## 7. Dependency management

- Centralize dependency composition in bootstrap/entrypoint modules.
- Keep business logic and services decoupled from the concrete environment.
- Avoid hidden service locators; make required collaborators explicit.
- Keep application logic separate from infrastructure details: business code should not directly know how the database, email, or side-effect adapters work.
- Prefer small factory functions or assembler classes if wiring becomes complex.
- Compose command buses, event handler registries, and adapters in one place whenever possible.
- Declare abstract dependencies in project metadata and capture concrete environment dependencies in a lock file or pinned requirements file for reproducible installs.
- Use minimum supported versions for dependencies where possible, but also maintain exact pinned environments for development and CI.
- Prefer the repository's `uv` managed environment and `uv sync` for local development workflows when the repository is configured for uv.
- Keep `requirements-dev.txt` in sync with repository dependency metadata when using requirements-based reproducible installs.
- Prefer minimal external dependencies; add packages only when the maintenance cost is justified.
- Pin production and development dependencies explicitly in requirements files or lock files so environments can be reproduced reliably.
- Use a dedicated virtual environment per project or the repository's `uv` managed environment to avoid dependency drift.

## 8. Error handling and logging

- Handle expected errors explicitly and fail fast on unexpected conditions.
- Do not swallow exceptions silently.
- Use Python's `logging` module for error, warning, info, and debug messages.
- Configure logging in bootstrap or entrypoint code, not during import time within library modules.
- Use structured logging with clear context for troubleshooting.
- Keep error-handling code separate from happy-path logic when possible.
- Prefer domain-specific exception types over generic exceptions.

## 9. Comments and documentation

- Write comments to explain why, not what.
- Prefer self-documenting code through clear names and structure.
- Use small helper methods instead of comments when the intent can be expressed in code.
- Use docstrings for public classes, functions, and modules.
- Document packages and modules with module-level docstrings and package docstrings in `__init__.py` where appropriate.
- Use docstring-driven documentation tools such as Sphinx, MkDocs + mkdocstrings, or FastAPI auto-generated docs for web APIs.
- Keep architecture and design decisions in `architecture/` and `prds/`.
- Update documentation when the architecture or package boundaries change.

## 10. Testing and validation

- Add tests for behavior, not implementation details.
- Cover boundary cases, data conversions, and failure modes.
- Keep tests small and focused on a single responsibility.
- Use typed models and parsers in tests to validate input and output shapes.
- Test service interactions through composable interfaces rather than global state.
- Prefer descriptive, scenario-style test names that document the expected behavior.
- Keep tests isolated from unrelated infrastructure and avoid broad integration in small modules when possible.
- Use doctests for simple examples where it keeps documentation and tests aligned.
- Prefer pytest for unit tests, and run tests in CI to keep regressions visible.
- Do not allow incomplete or placeholder tests to pass silently; fail fast with a clear assertion if a test is unfinished.

## 11. Formatting and linting

- Follow existing repository conventions and formatting.
- Use `ruff`/`mypy` for linting and type checking when available.
- Use `pyright` for CLI type checking; `pylance` is a VS Code language extension and is not runnable as `python -m pylance`.
- Use a code formatter or linter as part of development and CI to enforce consistent style.
- Use `pre-commit` or a similar hook system to run formatting and lint checks before commits.
- Prefer 4 spaces per indentation level; spaces are preferred over tabs and mixing tabs and spaces is forbidden.
- Keep imports grouped: standard library, third-party, local.
- Keep imports at the top of the file, after module docstrings and before module globals and constants.
- Use blank lines to separate top-level definitions (two blank lines) and class method definitions (one blank line).
- Avoid `from module import *`; prefer explicit imports or module-qualified names.
- Use absolute imports when practical; explicit relative imports are acceptable for complex package layouts.
- Avoid trailing whitespace.
- Keep line length reasonable (88-100 characters) unless readability favors a longer line; wrap docstrings and comments around 72 characters.
- Prefer module-level imports for local packages when possible; use symbol imports only when the package explicitly documents them or for third-party APIs.
- Use context managers (`with`) for files and other managed resources instead of manual cleanup.
- Prefer explicit code formatting over line-breaking that obscures intent.

## 12. Practical rules

- Prefer `dataclass` or `BaseModel` wrappers over raw dictionaries for domain data.
- Prefer immutable dataclasses for values that should not change after creation.
- Prefer helper classes for shared behavior instead of code duplication.
- Avoid hidden side effects in getters and short helper methods.
- Keep exception handling specific and avoid swallowing exceptions silently.
- Avoid deep coupling between GUI and business logic.
- Avoid `== True`, `== False`, and `== None` checks; prefer truthiness and identity comparisons such as `if attr`, `if not attr`, `if attr is None`, and `if attr is not None`.

## 13. Example culture

- `def parse_deposit_row(row: ScanSignatureCSVRowData) -> Optional[ScanSignature]:`
- `def build_capture_region(config: ConfigData) -> CaptureRegion:`
- `def _validate_anchor_templates(self) -> bool:`
- `def start_alignment_polling(self) -> None:`
- `def get_overlay_context(self) -> OverlayContext:`

These standards should guide ongoing work and future refactors without adding unnecessary complexity.
