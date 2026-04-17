# Code Quality and Linting Skill

Use this skill to run repository-level static analysis and linting in the `Scanning-Tool` repo. It collects actionable results from type checking, code style, and code-smell tools.

## When to use
- Before opening a PR to verify code quality.
- After refactors or dependency updates.
- When you want a concise, actionable report of issues from `mypy`, `ruff`, and related tooling.

## How to run
From the repository root, prefer the repo virtual environment commands:

```bash
.venv\Scripts\python.exe -m pyright .
.venv\Scripts\python.exe -m mypy .
.venv\Scripts\python.exe -m ruff check .
```

`pyright` is the CLI type checker; `pylance` is a VS Code language extension and cannot be invoked with `python -m pylance`.

If you need formatting feedback as well:

```bash
.venv\Scripts\python.exe -m ruff format . --check
```

If the virtual environment is not set up or the commands fail, fall back to the repo's managed Python setup:

```bash
uv run --managed-python --with-requirements requirements.txt -- python -m mypy .
uv run --managed-python --with-requirements requirements.txt -- python -m ruff check .
```

## What it does
1. Runs `mypy` across the repository to validate static typing.
2. Runs `ruff check .` to surface lint errors, code smells, complexity issues, and style violations.
3. Optionally checks whether formatting is required via `ruff format . --check`.

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
- `mypy` may need `--ignore-missing-imports` or repo-specific config if third-party stubs are missing.
- `ruff` can produce warnings for dynamic imports or generated code, so verify before changing code.
- A clean result from these tools is necessary but not sufficient; still run the test suite for behavior validation.

## Notes for LLM agents
- Use this skill whenever the task is about project-wide quality checks in `Scanning-Tool`.
- Prefer `.venv\Scripts\python.exe -m mypy .` and `.venv\Scripts\python.exe -m ruff check .` over manual file-by-file scanning.
- If the preferred commands fail, use the repo-managed `uv run --managed-python --with-requirements requirements.txt --` fallback.
- If the user asks for a report, return actionable items grouped by tool and severity.
