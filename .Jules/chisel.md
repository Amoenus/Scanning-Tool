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
## 2024-05-18 - [Handling Pydantic DTOs and kwargs in Event Handlers]
**Learning:** When refactoring event action handlers to use Pydantic models instead of raw dictionaries, it is necessary to ensure backward compatibility for callers that might pass a mix of DTOs, dicts, and kwargs. Dynamic `getattr` calls inside domain logic to access DTO fields contradict the strict typing goals.
**Action:** When migrating untyped payloads to DTOs in event handlers, always safely extract the dictionary representation (e.g., `payload.model_dump()` if it is a DTO, or `payload or {}` if it is a dict), merge it with `kwargs`, and then use `MyDTO.model_validate(merged_dict)`. In domain methods (`_payload_for_region`), explicitly type the input as a Union of the allowed DTOs, use `isinstance` checks, and access fields directly (with helper functions to supply defaults for missing optional values) rather than resorting to `Any` and `getattr`.
