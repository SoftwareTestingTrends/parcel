# One command per job. Every target exits non-zero on failure.
.PHONY: install test lint format chat

install:  ## install dependencies
	uv sync

test:  ## unit and end-to-end tests (offline mock, no model needed)
	uv run pytest

lint:  ## style and correctness checks (no changes made)
	uv run ruff check .
	uv run ruff format --check .

format:  ## auto-fix formatting
	uv run ruff check --fix .
	uv run ruff format .

chat:  ## talk to Parcel (set PARCEL_BACKEND first; mock by default)
	uv run parcel chat
