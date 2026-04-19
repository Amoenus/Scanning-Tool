# PRD: Web Server / WSGI Migration

## Purpose
This document defines the product requirements for migrating the scanning tool's browser overlay from Flask's built-in development server to a production-grade WSGI server.

## Problem Statement
The current overlay server is started with `flask_app.run(...)`, which uses Flask's built-in development server. That server prints a warning that it is not for production use, and it provides lower-quality request handling and fewer deployment options than a real WSGI server.

While the tool is currently a local desktop utility, the warning is noisy and the architecture is not clearly separated from the web server implementation. This makes future reuse, packaging, or transition to a more robust deployment model harder than necessary.

## Goals
- Remove the dependence on the Flask development server for the overlay.
- Expose the existing Flask app through a WSGI-compatible startup path.
- Keep local desktop usage unchanged in behavior and user experience.
- Allow the overlay server to be started with a WSGI server implementation while retaining a simple fallback for development.
- Keep the migration small, low-risk, and reversible.

## Scope
### In scope
- Add an explicit web server startup abstraction for the overlay service.
- Replace `flask_app.run(...)` with a WSGI server call in the existing startup flow.
- Use a lightweight WSGI implementation such as `waitress` or another compatible Python WSGI server.
- Add configuration or a runtime flag to choose between "development" and "production" server modes.
- Document the new startup path and update any relevant developer guidance.

### Out of scope
- Rewriting the web overlay UI, API contract, or business behavior.
- Converting the tool into a networked multi-user architecture.
- Adding remote or cloud deployment features.
- Replacing Flask entirely with another web framework.

## Success Criteria
- The overlay continues to render correctly at the configured host and port.
- The Flask development server warning is gone when the WSGI server path is used.
- The `create_app()` function in `src/scanning_tool/web/app.py` remains usable as a clean WSGI app factory.
- The local desktop startup flow remains stable and unchanged for normal development/test usage.
- The migration is documented in PRD and developer notes.

## Quality Requirements
- The migration must not introduce new runtime dependencies unless they are narrowly scoped and widely supported.
- The web server abstraction should keep the overlay app creation separate from server startup.
- The implementation should avoid adding global state or new startup complexity.
- The new server path should preserve existing logging and error handling behavior.

## Operation Model
1. `main.py` initializes config, runtime state, services, anchor tracking, and hotkey listeners.
2. `main.py` creates the Flask overlay app using `WebService.create_app()`.
3. The startup code passes the app to a `WebServer` abstraction that starts the chosen server implementation.
4. In normal local use, the runtime should behave the same as today; only the underlying server implementation changes.

## Implementation Approach
- Add a new module such as `src/scanning_tool/web/server.py`.
- Implement a small wrapper that accepts a Flask app, host, port, and a `use_wsgi` flag.
- Default to a WSGI server for normal startup while keeping a testable fallback to `flask_app.run(...)` when needed.
- Update `src/scanning_tool/main.py` to call the wrapper instead of `flask_app.run(...)` directly.
- Optionally add a `use_wsgiserver` config option to `web_server_config`.

## Risks and Mitigations
- Risk: introducing a new dependency can break packaging.
  - Mitigation: choose a stable dependency such as `waitress` and keep it optional if appropriate.
- Risk: the new startup path diverges from the local development experience.
  - Mitigation: preserve the old behavior as a fallback during migration.
- Risk: the web overlay app may behave differently under a WSGI server.
  - Mitigation: keep functional tests or manual verification focused on overlay rendering and status API.

## Notes
- Since this is a local tool today, the migration is primarily about removing the warning and future-proofing the server startup.
- The cleanest long-term architecture is to keep `create_app()` as a pure app factory and manage server choice separately.
- The migration should be low-effort and low-impact: a few lines of code in the startup path plus a small new module and optional config flag.
