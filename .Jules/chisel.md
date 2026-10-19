## 2024-10-19 - Strict DTOs for GUI Boundaries
**Learning:** Found a pattern where event payload dictionaries across `EditModeService` were manually and inconsistently parsed (e.g., using `_coerce_int_payload` and `.get()` manipulation).
**Action:** Replaced unstructured dictionaries with explicit Pydantic DTO models (`RegionDragPayload`, `RegionNudgePayload`, `RegionSelectPayload`) and `@model_validator` methods at the system boundary to standardize UI payload coercion and strictly enforce SOLID and strong typing principles.
