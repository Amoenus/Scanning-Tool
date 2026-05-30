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

## 2026-05-29 - Explicit DTO Validation at GUI Boundaries
**Learning:** Raw dictionary payloads (`dict[str, object]`) arriving from UI dispatch events obscure data requirements and bypass validation, leading to brittle `dict.get()` access in downstream handlers. Mypy also struggles when disparate Action Enums are merged into a single dictionary (like `ACTION_HANDLERS`) if strongly typed.
**Action:** Introduced strict Pydantic DTOs for each handler payload to deserialize inputs at the entry point via `.model_validate()`. Used `dict[object, Handler]` to safely unpack and aggregate diverse action enumeration keys without triggering mypy incompatibility errors.
