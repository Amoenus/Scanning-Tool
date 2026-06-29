## 2026-04-17 - Chisel Journal
**Learning:** The repo is using raw JSON-backed typed dicts for deposit ore data, which makes table-building logic harder to trace.
**Action:** Introduce a small typed DTO for ore stats and extract deposit table construction into focused helper methods.

## 2026-04-17 - Typed state defaults and explicit classmethod wiring
**Learning:** Runtime dataclass defaults must construct the correct domain model type, not a bare `dict`, so service state remains traceable and type-safe.
**Action:** Use `default_factory=RockDataCollection` for `RockData` state and implement explicit `SignatureRegistry.load_from_csv` behavior rather than a runtime monkey-patched stub.

## 2026-04-17 - Duplicate Domain Definitions
**Learning:** The domain model module contained duplicate class definitions for `OreStatistics`, `Deposit`, `Region`, and `RockDataCollection`, causing unnecessary ambiguity and reducing traceability.
**Action:** Keep a single authoritative domain model declaration per type to preserve clarity and avoid hidden runtime shadowing.

## 2026-05-11 - Parameter Object Refactor for Action Handlers
**Learning:** GUI action handlers suffered from parameter bloat (7 objects passed individually), making function signatures hard to read and brittle to add new dependencies to. This pattern of long parameter lists should be collapsed into a domain object.
**Action:** Introduced an `ActionContext` Parameter Object dataclass to encapsulate UI state dependencies, reducing handler signatures to simply accept `payload` and `context`, increasing traceability and SOLID compliance.

## 2026-05-31 - Pydantic Boundaries for Action Handler Payloads
**Learning:** GUI action handlers widely used unstructured `dict[str, object]` payloads requiring `.get()` and type coercion, bypassing static type checking and making the expected data shapes opaque.
**Action:** Replaced unstructured dictionaries with explicit Pydantic domain models (`TogglePayload`, `RegionUpdatePayload`, etc.) at the system boundary to enforce validation, type safety, and clear schema declarations.
## 2024-05-24 - [Strict Typing in GUI Payloads]
**Learning:** Event handlers using dynamic keyword arguments or `dict[str, object]` to receive payloads are prone to logic errors due to type mis-matches (like passing string coordinates when integers are expected), leading to manual, error-prone normalization and "cleaning" phases in application services like `EditModeService`.
**Action:** When refactoring event handlers that ingest loosely-typed dictionary payloads, enforce system boundaries by validating inputs directly against explicit Pydantic DTO models (e.g., `RegionDragPayload.model_validate(...)`). Always wrap `model_validate` in a `try...except ValidationError` block to short-circuit processing on bad input without bubbling exceptions to the main loop, matching the defensive programming pattern of the original code.

## 2024-05-24 - [Python 2 vs Python 3 Multiple Exception Syntax]
**Learning:** Found several old Python 2-style exception catches in `tk` components (e.g., `except tk.TclError, ValueError:`). Python 3 evaluates this as catching `tk.TclError` and binding the exception instance to the variable `ValueError`, which completely masks `ValueError`s and raises a `SyntaxError` on modern versions.
**Action:** When finding `except ExceptionA, ExceptionB:` patterns in legacy codebases, update them to the Python 3 tuple syntax: `except (ExceptionA, ExceptionB):`.
