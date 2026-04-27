# Domain Models Analysis

## Dataclass Optimizations (`slots=True`, `kw_only=True`, `frozen=True`)

*   `src/scanning_tool/domain/alignment.py`
    *   `CaptureRegion`: Already partially modernized.
    *   `AnchorDetection`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.
    *   `AlignmentInfo`: Needs `@dataclass(slots=True, kw_only=True)`. Cannot be frozen since properties change during state updates.
    *   `AlignmentRequest`: Already `frozen=True`. Needs `slots=True, kw_only=True`.

*   `src/scanning_tool/domain/ore_models.py`
    *   `Region`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.
    *   `RockDataCollection`: Needs `@dataclass(slots=True, kw_only=True)`.
    *   `OreTierInfo`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.

*   `src/scanning_tool/domain/capture.py`
    *   `DepositInfo`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.
    *   `ScanResult`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.
    *   `CodeExtraction`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.

*   `src/scanning_tool/domain/common.py`
    *   `Offset2D`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.
    *   `OreValueInfo`: Needs `slots=True, kw_only=True` (already frozen).
    *   `OreTableEntry`: Needs `@dataclass(frozen=True, slots=True, kw_only=True)`.

*   `src/scanning_tool/domain/scan_signature.py`
    *   `ScanSignature`: Needs `slots=True, kw_only=True` (already frozen).
    *   `ScanSignatureCSVRow`: Needs `slots=True, kw_only=True` (already frozen).

## `@cached_property` Opportunities

*   `src/scanning_tool/domain/scan_signature.py`: `ScanSignatureCSVRow.to_scan_signature()` could be a cached property.
*   `src/scanning_tool/domain/ore_models.py`: Properties wrapping `Deposit` stats could be cached properties.


## Value Object Opportunities

*   **Percentages:** In `OreStatistics` (`src/scanning_tool/domain/ore_models.py`), `prob`, `minPct`, `maxPct`, and `medPct` are raw `float` types. These represent probabilities and percentages, meaning they should be bounded between 0.0 and 1.0 (or 100.0). A `Percentage(float)` Value Object (similar to the ArjanCodes example) could centralize this invariant check.
*   **Scores and Thresholds:** In `AlignmentInfo`, `AnchorDetection`, and `AlignmentRequest` (`src/scanning_tool/domain/alignment.py`), the `score` and `threshold` are raw `float` types representing a confidence or matching threshold (likely bounded 0.0 to 1.0). A `Score(float)` Value Object would improve type safety.
*   **Counts:** In `Deposit` (`src/scanning_tool/domain/ore_models.py`), fields like `users`, `scans`, and `clusters` are `int` types, which theoretically should never be negative. A `NonNegativeInt(int)` Value Object could enforce this.

## State Machine Opportunities

*   `ScanState` (`src/scanning_tool/state/scan_state.py`):
    *   Currently relies on independent boolean flags like `is_scanning` and `continuous_mode`.
    *   This risks illegal state combinations (e.g., what if `is_scanning` is true while a shutdown happens?).
    *   Refactoring this into an explicit Enum-based State Machine (like `ScanStatus` with states `IDLE`, `SCANNING_SINGLE`, `SCANNING_CONTINUOUS`, `ERROR`) would ensure safe transitions and more predictable UI updates.


## Pythonic Refactoring Opportunities

*   **Modern Type Aliasing:** In `src/scanning_tool/domain/common.py`, `TypeAlias` is imported from `typing` and used as `RegionDepositTables: TypeAlias = ...`. Python 3.12 supports the modern explicit syntax: `type RegionDepositTables = dict[SpaceSystem, dict[str, DepositTable]]`.
*   **Pattern Matching (`match-case`):**
    *   In `src/scanning_tool/domain/parsers.py`, there are chained `if isinstance(value, ...)` blocks inside `parse_int`, `parse_float`, and `parse_str`. These are perfect candidates for Python 3.10+ `match` statements (e.g., `match value: case bool(): ... case int(): ...`).
    *   In `src/scanning_tool/ollama/installer.py`, `install_linux()` uses an `if-elif` chain to check OS release strings which could be simplified using pattern matching or a dictionary lookup strategy.

## Conclusion

This analysis has outlined several key areas for refactoring our python scanning tool to be more robust, pythonic, and safe using modern idioms documented by ArjanCodes (e.g. from the `2026/` example patterns). The current plan is to tackle the Dataclass Optimizations first, which has already been started. Next, Value Objects will be implemented for the primitives identified above.
