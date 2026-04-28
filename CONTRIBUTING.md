# Contributing

Thanks for helping improve ORCA.

## Setup

1. Clone the repo.
2. Sync the development environment using `uv`:
   ```bash
   uv sync
   ```
   If you need to install or update a dev package, use:
   ```bash
   uv add --dev <package>
   ```
   Keep `requirements-dev.txt` in sync for compatibility by regenerating or updating it after dependency changes.

## Code quality

- Format and lint with `ruff`:
  ```bash
  uv run --managed-python --with-requirements requirements-dev.txt -- ruff check ./src ./tests
  ```
- Run tests with `pytest`:
  ```bash
  uv run --managed-python --with-requirements requirements-dev.txt -- pytest -v tests
  ```
- Use pre-commit hooks:
  ```bash
  uv run --managed-python --with-requirements requirements-dev.txt -- pre-commit install
  ```

## Workflow

- Create a feature branch for each change.
- Open a PR against `main`.
- Keep PRs focused and include a short description of what changed.
- If your change affects user behavior, include testing notes in the PR.
