# PRD: Structured Logging Conversion

## Purpose

Define how the scanning tool will adopt a structured logging pattern across its console and file output, while preserving existing application behavior and developer ergonomics.

## Problem Statement

The application currently uses `loguru` for most internal logs, but Flask/Werkzeug request logs still appear in their default format. That produces uneven log output, and the codebase still contains unstructured string interpolation patterns that make diagnostics brittle and error-prone.

## Goals

- Standardize logging across the app so console output and log files use a single structured format.
- Route Flask/Werkzeug request logs through the same logging pipeline as application logs.
- Encourage structured log usage (`logger.info("event", region=region, code=code)`) instead of free-form message concatenation.
- Keep logs human-friendly on console while enabling metadata-rich output for debugging.
- Preserve existing log levels and runtime behavior.

## Scope

### In scope

- Centralizing logger setup in `src/scanning_tool/logging_setup.py`.
- Configuring `loguru` with a unified console and file sink.
- Intercepting standard library Flask/Werkzeug logging and forwarding it into `loguru`.
- Adding developer guidance for structured log messages in the repo docs or comments.
- Updating selected log emission sites to use `logger.bind(...)` or named fields where it is clearly beneficial.

### Out of scope

- Full OpenTelemetry instrumentation or exporter setup.
- Replacing `loguru` with another logging library.
- Converting every single existing log statement in one pass.
- Remote logging or backend telemetry pipelines.

## Requirements

- Logging configuration must be initialized once at application bootstrap.
- Flask and Werkzeug logs must appear with the same formatting as app logs.
- The console sink should remain readable by default.
- The file sink should preserve structured semantics for later parsing if desired.
- New structured log patterns should be easy for developers to adopt.
- Existing tests must continue to pass.

## Implementation approach

1. Use `loguru` as the canonical logger for the app.
2. Add a small intercept handler that forwards standard library logs into `loguru`.
3. Configure Flask/Werkzeug loggers to use that handler and disable propagation.
4. Keep the console format with timestamp, level, logger name, function, and line number.
5. Add guidance to prefer structured messages and keyword fields instead of raw formatted strings.
6. Optionally preserve a second sink for file-based logs with the same structured template.

## Success Criteria

- Console and file logs show a consistent `loguru`-based format.
- Flask/Werkzeug access logs no longer use the default Flask access log style.
- Structured metadata fields are available on key events.
- `pytest` passes without regressions in logging-sensitive tests.
- The implementation is localized to `logging_setup.py` and Flask startup wiring.

## Risks and mitigations

- `loguru` messages are already used in the codebase, so the core risk is adoption of the structured pattern.
  - Mitigation: document the preferred logging style and update a few representative sites.
- Some third-party Flask or library logs may still be emitted as raw strings.
  - Mitigation: intercept the main `werkzeug` logger and keep the default app logger attached.
- Strongly-typed structured logging can feel verbose if developers do not adopt keyword fields.
  - Mitigation: keep the guidance lightweight and focus on critical diagnostic events.

## Dependencies

- `loguru` is already part of the project.
- Flask/Werkzeug request logging should be wired through the intercept handler.
- No new external dependencies are required for this first phase.

## Future expansion

- If desired later, the structured logging foundation can be extended to JSON console output and OpenTelemetry export.
- The same structured events can feed a trace or log aggregation system if the project adopts OTEL in the future.
