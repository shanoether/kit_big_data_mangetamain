# Compialtion of bassh command to run before committing for linting, doc, formatting etc

uv sync
uv sync --group dev



# Run pyment once (if no file added) or ask copilot to add docstring to modified files
# Pyment write direclty into your files -> commit before running
uv run pyment -w -o google src/

# Go throught the files and check the docstring added (use copilot if necessary)

# Check coverage
uv run hatch run dev:docs-cov


# Libnintg with ruff etc

uv run ruff check . --statistics
uv run ruff check . --fix
uv run hatch run dev:lint --fix
uv run ruff format .
uv run isort .
uv run black .
uv run ruff check . --exclude notebook --exclude src/utils --exclude src/mypkg --exclude src/archive --exclude .venv --fix --unsafe-fixes
uv run ruff check .  # if folders excluded in pyproject.toml


# Create doc with mkdocs

# Addd missing dependencies if any
uv run add mkdocs-sections-index
uv add mkdocs-sections-index
uv add mkdocs-section-index
uv add pymdownx
uv add mkdocs-gen-files
uv add mkdocstrings
uv add mkdocstrings-python
uv add mkdocs-material
uv add mkdocs-literate-nav

uv run hatch run docs:serve