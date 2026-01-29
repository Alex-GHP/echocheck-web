.PHONY: check check-backend check-frontend

# Run all CI checks locally before pushing
check: check-backend check-frontend
	@echo ""
	@echo "✅ All CI checks passed! Safe to push."

check-backend:
	@echo "=== Backend Checks ==="
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	cd backend && uv run pytest --tb=short
	@echo ""

check-frontend:
	@echo "=== Frontend Checks ==="
	cd frontend && pnpm check
	cd frontend && pnpm exec tsc --noEmit
	cd frontend && pnpm test:run
	cd frontend && pnpm build
	@echo ""
