# Code checks. Configuration lives in pyproject.toml ([tool.ruff], [tool.pyright]).
# `make check` must pass before coding work counts as done (docs/CODING.md).

PATHS := src scripts tests

# uv warns when VIRTUAL_ENV points at another project's venv (it then uses this
# repo's .venv anyway); unexporting it only silences that noise.
unexport VIRTUAL_ENV

.PHONY: help check lint format-check typecheck test fix

help:
	@echo "make check         lint + format check + type check + tests (read-only)"
	@echo "make fix           apply ruff's safe lint fixes, then format"
	@echo "make lint | format-check | typecheck | test   one check each"

check: lint format-check typecheck test

lint:
	uv run ruff check $(PATHS)

format-check:
	uv run ruff format --check $(PATHS)

typecheck:
	uv run pyright

test:
	uv run pytest -q

fix:
	uv run ruff check --fix $(PATHS)
	uv run ruff format $(PATHS)
