.PHONY: help up down build logs migrate test lint format clean install dev

# Default target
help:
	@echo "FilterBets Development Commands"
	@echo "================================"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make up        - Start all services (docker-compose up -d)"
	@echo "  make down      - Stop all services (docker-compose down)"
	@echo "  make build     - Build all Docker images"
	@echo "  make logs      - View logs from all services"
	@echo "  make logs-b    - View backend logs only"
	@echo "  make logs-f    - View frontend logs only"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate   - Run database migrations"
	@echo "  make makemigrations MSG='message' - Create new migration"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install   - Install all dependencies (backend + frontend)"
	@echo "  make dev-b     - Run backend dev server locally"
	@echo "  make dev-f     - Run frontend dev server locally"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make test      - Run all tests"
	@echo "  make test-b    - Run backend tests only"
	@echo "  make test-f    - Run frontend tests only"
	@echo "  make lint      - Run all linters"
	@echo "  make lint-b    - Run backend linter (ruff)"
	@echo "  make lint-f    - Run frontend linter (eslint)"
	@echo "  make format    - Format all code"
	@echo "  make typecheck - Run type checkers"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean     - Remove build artifacts and caches"

# ===========================================
# Docker Commands
# ===========================================
up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

logs-b:
	docker-compose logs -f backend

logs-f:
	docker-compose logs -f frontend

# ===========================================
# Database Commands
# ===========================================
migrate:
	cd backend && poetry run alembic upgrade head

makemigrations:
	cd backend && poetry run alembic revision --autogenerate -m "$(MSG)"

# ===========================================
# Development Commands
# ===========================================
install:
	cd backend && poetry install
	cd frontend && pnpm install

dev-b:
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-f:
	cd frontend && pnpm dev

# ===========================================
# Quality Commands
# ===========================================
test: test-b test-f

test-b:
	cd backend && poetry run pytest tests/ -v

test-f:
	cd frontend && pnpm test --run

lint: lint-b lint-f

lint-b:
	cd backend && poetry run ruff check .

lint-f:
	cd frontend && pnpm lint

format:
	cd backend && poetry run ruff format .
	cd frontend && pnpm format

typecheck:
	cd backend && poetry run mypy app/
	cd frontend && pnpm typecheck

# ===========================================
# Cleanup Commands
# ===========================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
