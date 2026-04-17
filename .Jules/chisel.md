## 2026-04-17 - Chisel Journal
**Learning:** The repo is using raw JSON-backed typed dicts for deposit ore data, which makes table-building logic harder to trace.
**Action:** Introduce a small typed DTO for ore stats and extract deposit table construction into focused helper methods.
