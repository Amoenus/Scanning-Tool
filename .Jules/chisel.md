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

## 2024-07-06 - Pydantic Validation on System Boundaries
**Learning:** The `EditModeService` was manually parsing unstructured dictionaries for critical domain boundaries (UI events) using string lookups and `get()`, bypassing strict typing guarantees and failing to enforce schema conformance. Pydantic models with `model_validate()` and generic `try-except ValidationError` blocks gracefully absorb unexpected unstructured data while enforcing domain shape instantly upon receipt without crashing the application event bus.
**Action:** Always intercept `dict` payloads at system boundaries with explicit Pydantic DTOs and `model_validate`, using exception handling to act defensively instead of manual `dict.get()` normalization logic.
