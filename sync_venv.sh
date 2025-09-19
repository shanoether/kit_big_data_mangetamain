uv sync                 # install deps + lock
uv run ruff check .	# check for format error 
uv run ruff format .    # correct format error or add black and use it instead
uv run mypy .		# type checker to see consistence
uv run pytest		# run unit tests that are in tests/
uv build                # build wheel + sdist in dist/
