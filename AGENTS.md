# ORCA

ORCA is the Star Citizen ore reconnaissance and classification assistant.

## Development Setup

```bash
# Sync the project environment
uv sync

# Install or update a dev dependency
uv add --dev <package>

# Install pre-commit hooks
uv run --managed-python --with-requirements requirements-dev.txt -- pre-commit install

# Lint
uv run --managed-python --with-requirements requirements-dev.txt -- ruff check ./src ./tests

# Format
uv run --managed-python --with-requirements requirements-dev.txt -- ruff format ./src ./tests

# Run tests
uv run --managed-python --with-requirements requirements-dev.txt -- pytest -v tests

# Run local CI checks
uv run --managed-python --with-requirements requirements-dev.txt -- taskipy ci
```

## Tech Layers

- **Language**: Python 3.14+
- **Package manager**: uv
- **Build backend**: hatchling
- **Testing**: pytest
- **Linting**: ruff
- **Pre-commit hooks**: pre-commit

## Project Structure

```
src/
├── scanning_tool/      # Main app package
tests/                 # Test suite
pyproject.toml         # Project configuration and dependency groups
requirements-dev.txt   # Development dependencies
README.md              # Project overview and setup
CONTRIBUTING.md        # Contribution guidelines
```

## Development Guidelines

### Key Principles

- DO: Keep changes small and focused.
- DO: Prefer readability and maintainability.
- DO: Add tests for new features and bug fixes.
- DO: Follow existing project patterns.
- DO: Use type hints for new public APIs.
- DON'T: Add large speculative changes without review.

### Testing Approach

- Put tests in the `tests/` directory.
- Tests should pass with `uv run --managed-python --with-requirements requirements-dev.txt -- pytest -v tests`.
- Use `taskipy` tasks for local workflows when practical.

### Naming Conventions

- Constants: `SCREAMING_SNAKE_CASE`
- Functions/variables: `snake_case`
- Classes: `PascalCase`

### File Organization

- Group related functionality in `src/scanning_tool/`.
- Prefer small modules over large monolithic files.

### Safety and Permissions

Allowed without prompt:

- Reading files and listing directories
- Running single-file Python scripts, linting, formatting, and unit tests

Ask first:

- Installing new packages
- Pushing branches or making large repo-wide changes
- Deleting files or changing executable permissions
- Running full build or end-to-end suites

### When stuck

- Ask a clarifying question
- Propose a short plan before making broad changes
- Avoid large speculative edits without confirmation
