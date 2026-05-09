## 2026-04-17 - Chisel Journal
**Learning:** The repo is using raw JSON-backed typed dicts for deposit ore data, which makes table-building logic harder to trace.
**Action:** Introduce a small typed DTO for ore stats and extract deposit table construction into focused helper methods.

## 2026-04-17 - Typed state defaults and explicit classmethod wiring
**Learning:** Runtime dataclass defaults must construct the correct domain model type, not a bare `dict`, so service state remains traceable and type-safe.
**Action:** Use `default_factory=RockDataCollection` for `RockData` state and implement explicit `SignatureRegistry.load_from_csv` behavior rather than a runtime monkey-patched stub.

## 2026-04-17 - Duplicate Domain Definitions
**Learning:** The domain model module contained duplicate class definitions for `OreStatistics`, `Deposit`, `Region`, and `RockDataCollection`, causing unnecessary ambiguity and reducing traceability.
**Action:** Keep a single authoritative domain model declaration per type to preserve clarity and avoid hidden runtime shadowing.
## 2026-04-17 - ActionContext DTO encapsulates scattered handler dependencies
**Learning:** GUI action handlers suffered from the "Long Parameter List" code smell (taking 7 distinct state and service parameters), making testing and tracing difficult and violating encapsulation.
**Action:** Introduced a frozen, slotted `ActionContext` DTO in `src/scanning_tool/gui/context.py` to aggregate these dependencies into a single strongly-typed Parameter Object, applying this structural refactoring across all files in `src/scanning_tool/gui/handlers/`.
