# Dead Code Scan Skill

Use this skill to identify potentially unused Python modules and dead code in the `Scanning-Tool` repository. It combines a repo-specific static import scan with Vulture's dead-code analysis.

## When to use
- After large refactors affecting module structure or imports
- Before deleting a file or package to confirm it is not referenced
- When you suspect dead code remains after cleanup

## How to run
From the repository root:

```bash
python tools/dead_code_scan.py
```

To skip the Vulture pass and run only the import-based module scan:

```bash
python tools/dead_code_scan.py --no-vulture
```

## What it does
1. Scans all `*.py` files under `src/scanning_tool`
2. Builds a map of static `import` and `from ... import ...` references across the repo
3. Reports modules in `src/scanning_tool` that are not referenced by any other source file
4. Runs Vulture over `src/scanning_tool` to report functions, classes, and imports that appear unused

## Expected output
- `Candidate unused modules:` — modules that have no import references in the repo
- `Total module candidates:` — number of candidate unused modules
- `Vulture dead-code candidates:` — Vulture-flagged unused symbols

## Recommended workflow
1. Run the tool.
2. Review candidate modules and symbols.
3. Verify each candidate manually before deleting it, especially for dynamic imports or loader-based modules.
4. If a module is truly dead, remove it and rerun the tool.

## Gotchas
- Dynamic imports, plugin loading, or `__getattr__`-based exports may produce false positives.
- The import scan only catches static imports, so some live modules can still appear unused.
- Vulture can also report false positives for code paths only executed reflectively.

## Tool installation
This repo already added Vulture as a dev dependency with `uv add --dev vulture`.
If Vulture is not available, you can still use the import scan with `--no-vulture`.

## Notes for LLM agents
- Use this skill when the task is specifically about cleaning up dead Python code in `Scanning-Tool`.
- Prefer this tool over manual search for broad repository analysis.
- If the tool reports no candidates, the repo has no obvious whole-module dead code from static imports.
