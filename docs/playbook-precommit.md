# Pre-Commit Workflow Playbook

This playbook provides a comprehensive guide for running linting, formatting, testing, and documentation commands before committing code.

## Table of Contents
- [Quick Start](#quick-start)
- [Code Documentation](#code-documentation)
- [Linting and Formatting](#linting-and-formatting)
- [Testing and Coverage](#testing-and-coverage)
- [Documentation Generation](#documentation-generation)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [Workflow Summary](#workflow-summary)

---

## Quick Start

### Essential Commands

```bash
# 1. Sync dependencies
uv sync
uv sync --group dev

# 2. Format code
uv run ruff format .
uv run isort .
uv run black .

# 3. Check for issues
uv run ruff check . --fix

# 4. Run tests
uv run pytest

# 5. Generate documentation
uv run hatch run docs:serve
```

---

## Code Documentation

### Generate Docstrings with Pyment

**⚠️ WARNING**: Pyment writes directly to your files. Commit your changes before running!

```bash
# Generate Google-style docstrings for entire src/ directory
uv run pyment -w -o google src/
```

**After running Pyment**:
1. Review all modified files carefully
2. Check that docstrings are accurate and complete
3. Use GitHub Copilot to improve docstrings if needed
4. Fix any formatting issues

### Check Documentation Coverage

```bash
# Run documentation coverage check
uv run hatch run dev:docs-cov
```

This command analyzes how much of your code has proper documentation.

---

## Linting and Formatting

### Code Quality Checks

```bash
# Check for linting issues with statistics
uv run ruff check . --statistics

# Auto-fix linting issues
uv run ruff check . --fix

# Fix issues with Hatch dev environment
uv run hatch run dev:lint --fix
```

### Code Formatting

```bash
# Format code with Ruff (recommended)
uv run ruff format .

# Sort imports
uv run isort .

# Format with Black
uv run black .
```

### Advanced Ruff Usage

**With folder exclusions** (if folders are excluded in `pyproject.toml`):
```bash
uv run ruff check .
```

**Manual folder exclusions**:
```bash
uv run ruff check . \
  --exclude notebook \
  --exclude src/utils \
  --exclude src/mypkg \
  --exclude src/archive \
  --exclude .venv \
  --fix \
  --unsafe-fixes
```

### Linting Order of Operations

Recommended sequence for clean code:

1. **Format first**:
   ```bash
   uv run ruff format .
   uv run isort .
   uv run black .
   ```

2. **Then check and fix issues**:
   ```bash
   uv run ruff check . --fix
   ```

3. **Finally, verify**:
   ```bash
   uv run ruff check . --statistics
   ```

---

## Testing and Coverage

### Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run coverage run -m pytest && uv run coverage report -m

# Alternative syntax (if 'ur' alias is configured)
ur coverage run -m pytest && ur coverage report -m
```

### Run Specific Tests

```bash
# Run a specific test file
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py

# Run a specific test class
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py::TestRecipeAnalyzer

# Run a specific test method
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py::TestRecipeAnalyzer::test_compare_frequency_and_tfidf_returns_figure
```

### Clear Test Cache

If tests are failing unexpectedly:

```bash
# Remove pytest cache
rm -rf tests/unit/mangetamain/backend/__pycache__

# Rerun tests
uv run coverage run -m pytest && uv run coverage report -m
```

### Coverage Best Practices

- Aim for **80%+ coverage** on core business logic
- Check coverage report to identify untested code
- Add tests for edge cases and error handling

---

## Documentation Generation

### Install MkDocs Dependencies

If any dependencies are missing:

```bash
# Core documentation packages
uv add mkdocs-material
uv add mkdocstrings
uv add mkdocstrings-python
uv add mkdocs-gen-files
uv add mkdocs-literate-nav
uv add mkdocs-section-index
uv add pymdownx
```

Note: Try different variations if package names differ:
- `mkdocs-sections-index`
- `mkdocs-section-index`

### Serve Documentation Locally

```bash
# Start local documentation server
uv run hatch run docs:serve
```

This will typically serve documentation at `http://127.0.0.1:8000`.

### Build Documentation

```bash
# Build static documentation site
uv run mkdocs build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

---

## Pre-Commit Hooks

### Install Pre-Commit

```bash
# Add pre-commit to project
uv add pre-commit

# Install Git hooks
pre-commit install
```

### Run Pre-Commit

```bash
# Run on all files
pre-commit run --all-files

# Run automatically on git commit
git commit -m "your message"
```

### Bypass Pre-Commit (Use Sparingly)

```bash
# Skip pre-commit hooks (not recommended)
git commit -n -m "emergency fix"
# or
git commit --no-verify -m "emergency fix"
```

**⚠️ Only bypass pre-commit for**:
- Critical hotfixes
- Emergency production issues
- Work-in-progress commits on feature branches

---

## Workflow Summary

### Full Pre-Commit Checklist

Run these commands in order before committing:

```bash
# 1. Sync dependencies
uv sync --group dev

# 2. Generate/update docstrings (once or after adding files)
# ⚠️ Commit before running!
uv run pyment -w -o google src/

# 3. Review docstrings manually
# Use GitHub Copilot for improvements

# 4. Check documentation coverage
uv run hatch run dev:docs-cov

# 5. Format code
uv run ruff format .
uv run isort .
uv run black .

# 6. Fix linting issues
uv run ruff check . --fix
uv run hatch run dev:lint --fix

# 7. Run tests with coverage
uv run coverage run -m pytest && uv run coverage report -m

# 8. Verify no linting issues remain
uv run ruff check . --statistics

# 9. Serve documentation to verify
uv run hatch run docs:serve

# 10. Commit changes
git add .
git commit -m "descriptive commit message"
```

### Quick Pre-Commit (Minimal)

For smaller changes:

```bash
# Format and fix
uv run ruff format .
uv run ruff check . --fix

# Test
uv run pytest

# Commit
git commit -m "message"
```

---

## Configuration Files

### pyproject.toml

Ensure your `pyproject.toml` includes:

```toml
[tool.ruff]
exclude = [
    ".venv",
    "notebook",
    "src/archive",
]

[tool.ruff.lint]
select = ["E", "F", "I"]  # Error, Flake8, Import sorting

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

### Install pre-commit hook

#### Then install the precommit
```
uv install pre-commit
uv add pre-commit
pre-commit install
pre-commit run --all-files
```

#### avoid precommit with
```
git commit -nm 'my message'
````

### .pre-commit-config.yaml

Example pre-commit configuration:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

---

## Tips and Best Practices

1. **Run linters frequently** during development, not just before commits

2. **Use auto-fix carefully**: Review changes made by `--fix` flags

3. **Keep tests fast**: Slow tests discourage running them frequently

4. **Document complex logic**: Focus docstring efforts on non-obvious code

5. **Commit formatting separately**: Makes code review easier
   ```bash
   git commit -m "style: format code with ruff and black"
   git commit -m "feat: add new feature X"
   ```

6. **Use coverage to find gaps**: Don't just aim for high numbers; test meaningful scenarios

7. **Update documentation**: Keep MkDocs content in sync with code changes
