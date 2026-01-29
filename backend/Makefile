.PHONY: help dev test test-cov lint lint-fix format check install clean

help:
	@echo "EchoCheck Backend - Available commands:"
	@echo ""
	@echo "  make dev        - Start development server"
	@echo "  make test       - Run tests"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make lint       - Run linter (ruff check)"
	@echo "  make lint-fix   - Run linter and auto-fix"
	@echo "  make format     - Format code (ruff format)"
	@echo "  make check      - Run all checks (lint + format check)"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean cache files"
	@echo ""

dev:
	uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=term --cov-report=html

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .

install:
	uv sync --all-extras

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
