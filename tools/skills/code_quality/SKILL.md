# Code Quality and Linting Skill

Use this skill to run repository-level static analysis and linting in the `Scanning-Tool` repo. It collects actionable results from type checking, code style, and code-smell tools.

## When to use
- Before opening a PR to verify code quality.
- After refactors or dependency updates.
- When you want a concise, actionable report of issues from `mypy`, `ruff`, and related tooling.

## How to run
From the repository root, prefer the repo-managed `uv` workflow:

```bash
uv sync
uv run --managed-python --with-requirements requirements-dev.txt -- pyright .
uv run --managed-python --with-requirements requirements-dev.txt -- mypy src
uv run --managed-python --with-requirements requirements-dev.txt -- ruff check .
```

`pyright` is the CLI type checker; `pylance` is a VS Code language extension and cannot be invoked with `python -m pylance`.

If you need formatting feedback as well:

```bash
uv run --managed-python --with-requirements requirements-dev.txt -- ruff format . --check
```

If the repo-managed environment is not available, a manual virtual environment may be used as a fallback:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/macOS
python -m pip install -r requirements-dev.txt
python -m mypy src
python -m ruff check .
```

## What it does
1. Runs `pyright` across the repository to validate imports, module resolution, and narrow type assignments.
2. Runs `mypy` across the repository to validate static typing.
3. Runs `ruff check .` to surface lint errors, code smells, complexity issues, and style violations.
4. Optionally checks whether formatting is required via `ruff format . --check`.

## Expected output
- `mypy` reports type errors, missing imports, invalid assignments, and protocol mismatches.
- `ruff` reports syntax issues, unused imports/variables, complexity warnings, illegal patterns, and formatting concerns.
- `ruff format . --check` indicates whether source files need formatting.

## Recommended workflow
1. Run the tools.
2. Review reported issues and classify them as:
   - type-safety issues (`mypy`)
   - code-style/code-smell issues (`ruff`)
   - formatting required (`ruff format . --check`)
3. Fix true positives, then rerun the same commands.
4. Re-run tests after cleanup to verify behavior.

## Gotchas
- `pyright` may report missing imports if the virtual environment is not fully installed or if the repo path is not configured correctly.
- `mypy` may need `--ignore-missing-imports` or repo-specific config if third-party stubs are missing.
- `ruff` can produce warnings for dynamic imports or generated code, so verify before changing code.
- Prefer narrow types and explicit domain models instead of suppressing issues with `Any`.
- A clean result from these tools is necessary but not sufficient; still run the test suite for behavior validation.

## Notes for LLM agents
- Use this skill whenever the task is about project-wide quality checks in `Scanning-Tool`.
- Prefer `uv sync` and `uv run --managed-python --with-requirements requirements-dev.txt --` commands over manual venv commands.
- If the preferred commands fail, use a manual virtual environment fallback or report the environment issue clearly.
- If the user asks for a report, return actionable items grouped by tool and severity.
