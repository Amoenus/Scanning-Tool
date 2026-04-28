# PRD: Domain Data Flow and Class Structure

## Purpose

This document defines a clear architecture for how domain data is defined, validated, and transferred between packages in the Scanning Tool. It establishes a disciplined division between raw input shapes, pure business models, service logic, runtime state, and presentation data.

## Problem Statement

The repository currently has an unclear domain layer:

- `src/scanning_tool/domain/models.py` contains a broad mixture of data classes, DTO helpers, parsing helpers, presentation geometry, and configuration-bound classes.
- `src/scanning_tool/domain/dtos.py` is the only dedicated DTO module, but raw shapes are still scattered elsewhere.
- Several loose dataclasses exist in `gui/`, `state/`, `core/`, and `ollama/`, making it difficult to know which classes are pure domain values and which represent runtime or adapter state.
- The data flow between logical units is not explicit, which means developers cannot reliably tell whether a value is safe to mutate, whether it came from external input, or whether it belongs in the domain model.

This ambiguity reduces maintainability, impedes testability, and makes safe refactoring much harder.

## Goals

- Define explicit, non-overlapping class ownership for each architectural layer.
- Use typed data contracts for all inputs and outputs at package boundaries.
- Preserve pure domain semantics for business models and keep infrastructure concerns out of domain types.
- Make every transformation boundary explicit by naming conversion methods and adapters.
- Keep runtime state separate from domain models, especially for UI geometry, overlay state, and service process metadata.
- Enable a stable, testable architecture that can be extended without changing the core domain model.

## Target architecture

### Layer 1: External Input / DTOs

What it contains:
- raw CSV row shapes
- raw JSON shapes from `RockType.json`
- external config payloads
- raw strings from OCR
- mss monitor dictionaries
- request/response shapes for the web overlay

Goals for this layer:
- represent external, untrusted data exactly as it appears
- avoid business logic here
- keep shapes small and typed using `TypedDict`, low-level dataclasses, or Pydantic models for external contracts

Example artifacts:
- `domain/dtos.py`
- `config/models.py` or `config/dtos.py`
- `ollama/prompt.py` for prompt metadata if it maps to external model behavior

### Layer 2: Domain Models

What it contains:
- business value objects with invariants
- aggregation of typed data that represents core concepts
- conversion methods from DTOs or adapter inputs

Goals for this layer:
- make models immutable wherever possible
- keep domain types free of side effects and framework dependencies
- use explicit constructors such as `from_dict`, `from_mapping`, or `from_config`

Example artifacts:
- `domain/scan_signature.py`
- `domain/ore.py`
- `domain/alignment.py`
- `domain/capture.py`
- `domain/result.py`
- `domain/common.py`

### Layer 3: Application / Services

What it contains:
- reusable workflow logic
- repository interfaces / domain services
- conversion between domain models and adapter outputs

Goals for this layer:
- operate on domain objects, not raw dictionaries
- accept dependencies explicitly through constructors or factory methods
- isolate infrastructure adapters behind small service boundaries
- separate command handling from event handling and keep workflow orchestration out of pure domain code

Example artifacts:
- `services/capture_service.py`
- `services/alignment_service.py`
- `services/ollama_service.py`
- `services/message_bus.py`
- `deposits/scan_signatures.py`
- `deposits/lookup.py`
- `core/anchor/anchor_matcher.py`

### Layer 4: Runtime State

What it contains:
- mutable application state only while the app is running
- caches, progress flags, temporary state, and UI toggles
- process handles and service lifecycle metadata

Goals for this layer:
- avoid placing domain model business data here unless it is truly transient
- keep state objects narrow and purpose-specific
- make the state layer injectable or at least easier to replace/mocking in tests
- keep runtime state separate from command handling and event-driven workflows

Example artifacts:
- `state/service_state.py`
- `state/scan_state.py`
- `gui/overlay_state.py`
- `gui/control_state.py`

### Layer 5: Presentation / UI

What it contains:
- rendering decisions
- presentation-only layout models
- GUI event handlers
- overlay window geometry and animation helpers

Goals for this layer:
- consume domain objects and render them without embedding domain logic
- keep UI models separate from domain models unless they are truly shared read-only values
- keep visualization-specific classes in `gui/` or `web/`

Example artifacts:
- `gui/sections/*.py`
- `gui/overlays/*.py`
- `web/app.py`

### Commands and Events
- Treat user-facing inputs and entrypoint requests as commands, and treat internal notifications as events.
- Use explicit, immutable command and event data shapes rather than passing raw data around.
- Keep command handlers responsible for state-changing work and event listeners responsible for side effects, logging, or read-model updates.
- Register handlers and wire adapters in bootstrap/entrypoint code, not inside domain classes.
- Prefer separate read-only views for queries, rather than reusing write-model workflows for presentation.
- Use `blinker` as the standard in-process signal library for internal event wiring in this repo.

## Proposed package structure

The following structure should become the canonical architecture for the repository:

```
src/scanning_tool/
    config/
        models.py            # typed settings and config validation
        service.py           # config loading/persistence
    domain/
        __init__.py          # explicit exports only
        dtos.py              # external wire shapes
        common.py            # shared value types and helper conversions
        scan_signature.py    # scan signature domain models and registry interface
        ore.py               # RockType, deposit, ore data models
        alignment.py         # alignment request/result models
        capture.py           # capture region and scan result models
    deposits/
        scan_signatures.py   # CSV loading adapter and registry bootstrap
        lookup.py            # code extraction and deposit lookup service
        tables.py            # deposit table formatting and serialization
        ore_tiers.py         # ore tier logic and display metadata
    services/
        capture_service.py   # capture/OCR pipeline orchestration
        alignment_service.py # alignment business logic
        ollama_service.py    # Ollama process lifecycle
        base_service.py      # service base class abstractions
    core/
        anchor/
            anchor_matcher.py
            anchor_region_tracker.py
            anchor_template_loader.py
    state/
        service_state.py
        scan_state.py
    gui/
        app.py
        assembler.py
        sections/
        overlays/
        widgets/
        control_state.py
        overlay_state.py
    ollama/
        host.py
        installer.py
        models.py
    web/
        app.py
```

## Clear ownership rules

### Domain models

Use domain models for business data only. If a class is used to represent a deposit, scan result, alignment request, or business lookup result, it belongs in `domain/`.

Do not store UI geometry, overlay layout, prompt selection, or runtime handles in domain classes.

### DTOs

Use DTOs for every external boundary:
- CSV rows
- parsed JSON from `RockType.json`
- raw OCR text
- external config values
- screen capture monitor data

DTOs are not business models. They are converters.

### Services

Service classes must depend on domain models and DTOs, not on raw dictionaries or global singleton state. A service can own a small adapter interface to infrastructure, but it should never own unrelated domain data.

### Runtime state

Runtime state should be explicit and narrow. If a value lives in `state/`, it must be application state only. Domain data should flow through the pipeline as read-only values whenever possible.

### Presentation / UI

The UI layer may define view-specific DTOs for rendering, but those should be built from domain objects. Example: `ScanResultViewModel` can be a small wrapper around `ScanResult` if needed, but the canonical model remains in `domain/`.

## Data flow guidance

### 1. Raw source → adapter → DTO

Examples:
- read `csv/scansig/scan_signatures_summary.csv`
- create `ScanSignatureCSVRowData` for each row
- convert to `ScanSignatureCSVRow` and then to domain `ScanSignature`

- read `RockType.json`
- treat the parsed JSON as raw `RockDataJSON`
- convert it into `OreStatistics`, `Deposit`, `Region`, and `RockDataCollection`

- receive raw OCR text
- pass it to `DepositCodeParser.extract_code`
- produce a typed `CodeExtraction`

### 2. DTO → domain model

Conversion methods should be explicit and centralized:
- `ScanSignatureCSVRow.from_mapping(...)`
- `Deposit.from_dict(...)`
- `AlignmentRequest.from_config(...)`
- `CaptureRegion.to_mss_monitor()`

The service layer should only accept domain objects once validation is complete.

### 3. Domain model → service operation

Example flow:

1. `CaptureService` obtains a `CaptureRegion` and an `AlignmentRequest` from config.
2. It captures an image and passes the pixels to `AnchorMatcher`.
3. `AnchorMatcher` returns an `AnchorDetection` domain object.
4. `CaptureService` uses `ocr_service.ocr_with_ollama(...)` to get raw text.
5. `DepositCodeParser` creates a `CodeExtraction` domain object.
6. `DepositLookupService` consumes the cleaned code and returns a `DepositInfo` domain object.
7. The GUI receives a `ScanResult` domain object and renders it.

### 4. Service output → presentation

Presentation should consume only read-only domain outputs.
- The GUI should render `ScanResult` and `DepositInfo` directly.
- The web overlay should consume the same domain objects or small view models built from them.
- UI state should be separate from business results.

## Suggested file ownership by class

### `domain/common.py`
- `Offset2D`
- `MssMonitor`
- shared literal types like `OreTier`

### `domain/scan_signature.py`
- `ScanSignature`
- `ScanSignatureCSVRow`
- `SignatureRegistry`

### `domain/ore.py`
- `OreStatistics`
- `Deposit`
- `Region`
- `RockDataCollection`
- `DepositTable` / table row models if they represent core data

### `domain/alignment.py`
- `AlignmentInfo`
- `AlignmentRequest`
- `AnchorDetection`
- `CaptureRegion`

### `domain/capture.py`
- `ScanResult`
- `DepositInfo`

### `domain/dtos.py`
- `ScanSignatureCSVRowData`
- `OreStatisticsData`
- `DepositData`
- any other raw wire shapes

## Proposed conversion conventions

- `from_mapping` for raw untyped input
- `from_dict` for generic JSON/dict conversions
- `to_scan_signature`, `to_mss_monitor`, `to_tuple` for value normalization
- use `@classmethod` constructors whenever domain invariants are required

## Success criteria

A refactor is complete when:

- `src/scanning_tool/domain/models.py` is no longer a catch-all file and has been replaced by explicit submodules.
- `src/scanning_tool/domain/dtos.py` contains only external/raw input shapes.
- No domain class in `domain/` depends on GUI, Flask, `tkinter`, or `mss` directly.
- `services/` and `deposits/` accept explicit domain objects instead of raw dictionaries or hidden global state.
- `state/` contains only runtime state, not pure business models, except where a state object wraps domain objects transiently.
- Presentation code reads domain outputs and does not reconstruct business models from raw dictionaries.
- Tests cover the boundary conversions and service flows explicitly.

## Quality requirements

- Every package boundary must be clearly documented in `architecture/README.md` and within the code.
- Keep all data transfer operations strongly typed.
- Avoid `Any` and generic `dict` types in public method signatures.
- Use immutable dataclasses for domain values whenever mutation is not required.
- Prefer constructor injection over global import-time state.
- Prefer composition over inheritance for adapters and services.
- Keep methods small: each transformation from raw input to domain object should be localized to a named helper.

## Implementation roadmap

1. Refactor `domain/models.py` into explicit submodules.
2. Keep `domain/dtos.py` as the raw input contract file and move any non-DTO types out of it.
3. Move presentation/layout and UI-only dataclasses out of domain into `gui/` or `state/`.
4. Move `ScanSignature`/`SignatureRegistry` into `domain/scan_signature.py` and use adapter-driven loading in `deposits/scan_signatures.py`.
5. Refactor `deposits/lookup.py` so it depends on a `SignatureRegistry` instance and a `DepositCodeParser`, not on global runtime state.
6. Review `ollama/host.py`, `ollama/models.py`, and `services/ocr_service.py` to keep only domain-relevant prompt/profile models in `domain/` if they are truly business-level; otherwise move them into `ollama/`.
7. Align `state/` and `gui/` packages so runtime state is clearly separated from domain and service code.
8. Update documentation and package exports so `domain/__init__.py` re-exports only the intended public domain symbols.

## Risks and assumptions

- The domain layer is assumed to be stable for the current product scope of deposit scanning and scan signature resolution.
- This PRD does not propose changing OCR behavior, capture algorithms, or external APIs; it only clarifies architecture and class division.
- Existing tests should guide the refactor and prevent behavioral drift.
- The architecture assumes a single-user desktop application and does not require multi-tenant or distributed overlay state.

## Decision points

- `domain/` must remain the source of truth for business concepts.
- `dtos.py` should never contain logic beyond conversion helpers.
- UI geometry and overlay layout classes belong in `gui/` or `state/`, not in `domain/`.
- Services should never directly import runtime manager globals for business-facing operations.
- Explicit constructor-based conversion is preferred over ad hoc data reshaping inside services.

## How to use this document

Use this PRD as the source of truth when:
- adding a new data model
- moving an existing class from one package to another
- defining the input shape for a new parser or external adapter
- writing new tests for data flow boundaries
- reviewing code for separation of concerns
