"""Identify candidate dead Python code using import coverage and Vulture."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "src" / "scanning_tool"
IMPORT_PATTERNS = [
    re.compile(r"from\s+([\w\.]+)\s+import"),
    re.compile(r"import\s+([\w\.]+)"),
]


def module_name(path: Path) -> str:
    rel = path.relative_to(SOURCE_ROOT).with_suffix("")
    return "scanning_tool." + ".".join(rel.parts)


def find_python_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def gather_imports(paths: Iterable[Path]) -> dict[str, set[Path]]:
    imports: dict[str, set[Path]] = {}
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue

        for pattern in IMPORT_PATTERNS:
            for match in pattern.finditer(content):
                imports.setdefault(match.group(1), set()).add(path)
    return imports


def find_unused_modules(source_root: Path) -> list[tuple[str, Path]]:
    imports = gather_imports(find_python_files(ROOT))
    unused: list[tuple[str, Path]] = []

    for path in find_python_files(source_root):
        if path.name in ("__init__.py", "__main__.py"):
            continue

        mod = module_name(path)
        if any(
            imported_mod == mod
            or imported_mod.startswith(mod + ".")
            or mod.startswith(imported_mod + ".")
            for imported_mod in imports
            if any(p != path for p in imports[imported_mod])
        ):
            continue

        unused.append((mod, path))

    return unused


def run_vulture(source_root: Path) -> list[str]:
    try:
        command = [sys.executable, "-m", "vulture", str(source_root)]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ["Vulture is not available in this interpreter."]

    output = result.stdout.strip()
    if not output:
        return ["Vulture found no dead code candidates."]

    return [line for line in output.splitlines() if line.strip()]


def print_section(title: str, lines: list[str]) -> None:
    print(f"{title}")
    if not lines:
        print("  None")
        return

    for line in lines:
        print(f"  {line}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan the repository for dead Python code using import analysis and Vulture.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=SOURCE_ROOT,
        help="Root source directory to analyze (default: src/scanning_tool).",
    )
    parser.add_argument(
        "--no-vulture",
        action="store_true",
        help="Skip the Vulture analysis pass and only run import-based module scanning.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = args.path.resolve()

    if not source_root.exists() or not source_root.is_dir():
        raise SystemExit(f"Source root not found: {source_root}")

    module_candidates = find_unused_modules(source_root)
    print_section(
        "Candidate unused modules:",
        [f"{mod} -> {path}" for mod, path in module_candidates],
    )
    print(f"\nTotal module candidates: {len(module_candidates)}\n")

    if not args.no_vulture:
        vulture_lines = run_vulture(source_root)
        print_section("Vulture dead-code candidates:", vulture_lines)


if __name__ == "__main__":
    main()
