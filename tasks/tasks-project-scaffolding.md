# Tasks: Project Scaffolding

## Relevant Files

### Backend

- `backend/app/__init__.py` - Package init for the FastAPI app module
- `backend/app/main.py` - FastAPI application entry point with routes and middleware
- `backend/app/config.py` - Pydantic Settings for environment variable management
- `backend/app/database.py` - Async SQLAlchemy engine and session factory
- `backend/alembic.ini` - Alembic configuration file
- `backend/alembic/env.py` - Alembic environment for async migrations
- `backend/alembic/script.py.mako` - Alembic migration template
- `backend/pyproject.toml` - Poetry dependencies and tool configuration
- `backend/Dockerfile` - Multi-stage Docker build for production
- `backend/.python-version` - Python version specification
- `backend/tests/__init__.py` - Test package init
- `backend/tests/conftest.py` - Pytest fixtures and configuration
- `backend/tests/test_health.py` - Tests for health endpoint

### Frontend

- `frontend/src/main.tsx` - React application entry point
- `frontend/src/App.tsx` - Root component with routing
- `frontend/src/index.css` - Global styles with Tailwind directives
- `frontend/src/api/client.ts` - Axios instance with interceptors
- `frontend/src/components/layout/Header.tsx` - Header layout component
- `frontend/src/pages/Home.tsx` - Home page component
- `frontend/src/pages/Login.tsx` - Login page placeholder
- `frontend/src/pages/NotFound.tsx` - 404 page component
- `frontend/index.html` - HTML entry point
- `frontend/package.json` - pnpm dependencies
- `frontend/vite.config.ts` - Vite configuration
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/tsconfig.node.json` - TypeScript config for Node
- `frontend/tailwind.config.js` - Tailwind CSS configuration
- `frontend/postcss.config.js` - PostCSS configuration
- `frontend/eslint.config.js` - ESLint flat config
- `frontend/.prettierrc` - Prettier configuration
- `frontend/Dockerfile` - Multi-stage Docker build with nginx
- `frontend/nginx.conf` - Nginx configuration for SPA
- `frontend/src/lib/utils.ts` - Utility functions (cn helper for shadcn)

### Infrastructure

- `docker-compose.yml` - Development Docker Compose configuration
- `docker-compose.prod.yml` - Production-like Docker Compose configuration
- `.env.example` - Environment variable template

### CI/CD

- `.github/workflows/ci.yml` - GitHub Actions CI pipeline

### Project Config

- `Makefile` - Common development commands
- `.gitignore` - Updated gitignore patterns
- `README.md` - Updated project documentation

### Notes

- Backend tests use `pytest` with async support via `pytest-asyncio`
- Frontend tests use `vitest` with React Testing Library
- Run `make test` to execute all tests after setup is complete
- Use `make up` to start all Docker services
- Use `make down` to stop all Docker services

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:

- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch `feature/project-scaffolding`

- [ ] 1.0 Set up Backend Foundation (FastAPI)
  - [x] 1.1 Create `backend/` directory structure (`app/`, `tests/`, `alembic/`)
  - [x] 1.2 Create `backend/.python-version` with `3.12`
  - [x] 1.3 Create `backend/pyproject.toml` with Poetry dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, alembic, pydantic-settings, redis, pytest, ruff, mypy)
  - [x] 1.4 Create `backend/app/__init__.py` (empty package init)
  - [x] 1.5 Create `backend/app/config.py` with Pydantic Settings class for environment variables
  - [x] 1.6 Create `backend/app/database.py` with async SQLAlchemy engine and session factory
  - [x] 1.7 Create `backend/app/main.py` with FastAPI app, CORS middleware, `/health` and `/` endpoints
  - [x] 1.8 Initialize Alembic with `alembic init alembic` and configure for async
  - [x] 1.9 Create `backend/alembic/env.py` configured for async SQLAlchemy
  - [x] 1.10 Create `backend/tests/__init__.py` and `backend/tests/conftest.py` with pytest fixtures
  - [x] 1.11 Create `backend/tests/test_health.py` with tests for health endpoint
  - [x] 1.12 Create `backend/Dockerfile` with multi-stage build
  - [x] 1.13 Configure ruff in `pyproject.toml` (linting rules, line length, target version)
  - [x] 1.14 Configure mypy in `pyproject.toml` (strict mode, async plugins)
  - [x] 1.15 Configure pytest in `pyproject.toml` (asyncio mode, coverage)
  - [ ] 1.16 Verify backend runs locally with `poetry install && poetry run uvicorn app.main:app --reload` (pending network connectivity)

- [ ] 2.0 Set up Frontend Foundation (React + Vite)
  - [ ] 2.1 Initialize Vite project with React + TypeScript template in `frontend/`
  - [ ] 2.2 Configure `frontend/package.json` with pnpm and all dependencies
  - [ ] 2.3 Install and configure Tailwind CSS (`tailwind.config.js`, `postcss.config.js`)
  - [ ] 2.4 Add Tailwind directives to `frontend/src/index.css`
  - [ ] 2.5 Initialize shadcn/ui and install base components (button, card, input)
  - [ ] 2.6 Create `frontend/src/lib/utils.ts` with `cn` helper function
  - [ ] 2.7 Configure TanStack Query in `frontend/src/main.tsx`
  - [ ] 2.8 Set up React Router in `frontend/src/App.tsx` with route definitions
  - [ ] 2.9 Create `frontend/src/api/client.ts` with axios instance and request/response interceptors
  - [ ] 2.10 Create `frontend/src/components/layout/Header.tsx` placeholder component
  - [ ] 2.11 Create `frontend/src/pages/Home.tsx` with basic dashboard placeholder
  - [ ] 2.12 Create `frontend/src/pages/Login.tsx` with login form placeholder
  - [ ] 2.13 Create `frontend/src/pages/NotFound.tsx` with 404 message
  - [ ] 2.14 Configure ESLint with `frontend/eslint.config.js` (flat config)
  - [ ] 2.15 Create `frontend/.prettierrc` with formatting rules
  - [ ] 2.16 Configure Vitest in `frontend/vite.config.ts`
  - [ ] 2.17 Create `frontend/Dockerfile` with multi-stage build (node build, nginx serve)
  - [ ] 2.18 Create `frontend/nginx.conf` for SPA routing
  - [ ] 2.19 Update `frontend/tsconfig.json` with strict mode and path aliases
  - [ ] 2.20 Verify frontend runs locally with `pnpm install && pnpm dev`

- [ ] 3.0 Set up Docker Infrastructure
  - [ ] 3.1 Create `docker-compose.yml` with services: db (postgres), redis, backend, frontend
  - [ ] 3.2 Configure PostgreSQL service with persistent volume and health check
  - [ ] 3.3 Configure Redis service with health check
  - [ ] 3.4 Configure backend service with volume mount for hot-reload and depends_on
  - [ ] 3.5 Configure frontend service with volume mount for hot-reload
  - [ ] 3.6 Create `docker-compose.prod.yml` for production-like environment
  - [ ] 3.7 Create `.env.example` with all required environment variables
  - [ ] 3.8 Create `.dockerignore` files for backend and frontend
  - [ ] 3.9 Verify `docker-compose up` starts all services successfully

- [ ] 4.0 Set up CI/CD Pipeline (GitHub Actions)
  - [ ] 4.1 Create `.github/workflows/` directory
  - [ ] 4.2 Create `.github/workflows/ci.yml` with trigger on push/PR to main
  - [ ] 4.3 Add job for backend linting (`ruff check backend/`)
  - [ ] 4.4 Add job for backend type checking (`mypy backend/`)
  - [ ] 4.5 Add job for backend tests (`pytest backend/tests/`)
  - [ ] 4.6 Add job for frontend linting (`pnpm lint`)
  - [ ] 4.7 Add job for frontend type checking (`pnpm typecheck`)
  - [ ] 4.8 Add job for frontend tests (`pnpm test`)
  - [ ] 4.9 Configure dependency caching (Poetry cache, pnpm cache)
  - [ ] 4.10 Add PostgreSQL service container for backend tests

- [ ] 5.0 Create Project Configuration & Documentation
  - [ ] 5.1 Create `Makefile` with targets: up, down, build, migrate, test, lint, logs
  - [ ] 5.2 Update root `.gitignore` with comprehensive patterns (venv, node_modules, .env, **pycache**, etc.)
  - [ ] 5.3 Update `README.md` with project overview, setup instructions, and available commands
  - [ ] 5.4 Create `.pre-commit-config.yaml` for pre-commit hooks (ruff, mypy, eslint)

- [ ] 6.0 Verify Full Stack Integration
  - [ ] 6.1 Run `make up` and verify all containers start without errors
  - [ ] 6.2 Verify backend health check at `http://localhost:8000/health`
  - [ ] 6.3 Verify frontend loads at `http://localhost:5173`
  - [ ] 6.4 Verify frontend can call backend API (CORS working)
  - [ ] 6.5 Run `make test` and verify all tests pass
  - [ ] 6.6 Run `make lint` and verify no linting errors
  - [ ] 6.7 Commit all changes with message `feat: add project scaffolding with FastAPI, React, and Docker`
