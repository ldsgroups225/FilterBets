# PRD: Project Scaffolding

## 1. Introduction/Overview

This PRD covers the initial project scaffolding for FilterBets - a football betting analytics platform. The goal is to establish a solid monorepo foundation with a FastAPI backend, React frontend, and Docker-based development environment that's structured for easy cloud migration.

**Problem:** The project currently only has a data download script and documentation. There's no application structure, no database, and no way to run the platform.

**Solution:** Create the complete project skeleton with all necessary configurations, dependencies, and Docker services to enable rapid feature development.

## 2. Goals

| Goal | Measurable Outcome |
| ------ | ------------------- |
| Backend foundation | FastAPI app running on `localhost:8000` with health endpoint |
| Frontend foundation | React app running on `localhost:5173` with basic routing |
| Database ready | PostgreSQL accessible and migrations working |
| Cache/broker ready | Redis running and connectable |
| Developer experience | Single `docker-compose up` starts all services |
| CI/CD foundation | GitHub Actions runs linting and tests on PR |
| Cloud-ready structure | Environment-based configs, Dockerfiles optimized for production |

## 3. User Stories

### Developer Stories

- **As a developer**, I want to run `docker-compose up` and have all services start, so I can begin coding immediately.
- **As a developer**, I want hot-reload on both backend and frontend, so I can see changes without restarting.
- **As a developer**, I want pre-configured linting and type checking, so code quality is enforced from day one.
- **As a developer**, I want clear environment variable management, so I don't accidentally commit secrets.
- **As a developer**, I want the project structure to match industry standards, so onboarding new team members is easy.

## 4. Functional Requirements

### 4.1 Backend (FastAPI)

| ID | Requirement |
| ---- | ------------- |
| BE-01 | Create `backend/` directory with FastAPI application structure |
| BE-02 | Implement `app/main.py` with FastAPI app instance and CORS middleware |
| BE-03 | Implement `app/config.py` using Pydantic Settings for environment variables |
| BE-04 | Implement `app/database.py` with async SQLAlchemy engine and session factory |
| BE-05 | Create `GET /health` endpoint returning `{"status": "healthy", "database": "connected"}` |
| BE-06 | Create `GET /` endpoint returning API info (name, version, docs URL) |
| BE-07 | Configure `pyproject.toml` with all backend dependencies using Poetry |
| BE-08 | Create `backend/Dockerfile` optimized for production (multi-stage build) |
| BE-09 | Set up Alembic for database migrations with async support |
| BE-10 | Configure `ruff` for linting and formatting |
| BE-11 | Configure `mypy` for type checking with strict mode |
| BE-12 | Configure `pytest` with async support and coverage reporting |

### 4.2 Frontend (React)

| ID | Requirement |
| ---- | ------------- |
| FE-01 | Create `frontend/` directory with Vite + React + TypeScript |
| FE-02 | Configure Tailwind CSS with default theme |
| FE-03 | Install and configure shadcn/ui with essential components |
| FE-04 | Set up TanStack Query with default query client |
| FE-05 | Set up React Router v6 with basic route structure |
| FE-06 | Create `src/api/client.ts` with axios instance and interceptors |
| FE-07 | Create basic layout component (Header placeholder, main content area) |
| FE-08 | Create placeholder pages: Home, Login, NotFound |
| FE-09 | Create `frontend/Dockerfile` optimized for production (nginx) |
| FE-10 | Configure ESLint and Prettier |
| FE-11 | Configure Vitest for unit testing |

### 4.3 Infrastructure (Docker)

| ID | Requirement |
| ---- | ------------- |
| INF-01 | Create `docker-compose.yml` for local development |
| INF-02 | Configure PostgreSQL 16 service with persistent volume |
| INF-03 | Configure Redis 7 service |
| INF-04 | Configure backend service with hot-reload (volume mount) |
| INF-05 | Configure frontend service with hot-reload |
| INF-06 | Create `docker-compose.prod.yml` for production-like environment |
| INF-07 | Create `.env.example` with all required environment variables |
| INF-08 | Add `nginx.conf` for frontend production serving |

### 4.4 CI/CD (GitHub Actions)

| ID | Requirement |
| ---- | ------------- |
| CI-01 | Create `.github/workflows/ci.yml` for pull request checks |
| CI-02 | Run backend linting (`ruff check`) |
| CI-03 | Run backend type checking (`mypy`) |
| CI-04 | Run backend tests (`pytest`) |
| CI-05 | Run frontend linting (`eslint`) |
| CI-06 | Run frontend type checking (`tsc --noEmit`) |
| CI-07 | Run frontend tests (`vitest run`) |
| CI-08 | Cache dependencies (Poetry, pnpm) for faster builds |

### 4.5 Project Configuration

| ID | Requirement |
| ---- | ------------- |
| CFG-01 | Update root `pyproject.toml` to be workspace-aware |
| CFG-02 | Create `backend/pyproject.toml` with backend-specific dependencies |
| CFG-03 | Update `.gitignore` with comprehensive patterns |
| CFG-04 | Create `Makefile` with common commands (up, down, migrate, test, lint) |

## 5. Non-Goals (Out of Scope)

- **No authentication implementation** - just placeholder pages
- **No database models** - only connection setup (Phase 1.2)
- **No data ingestion** - separate phase (Phase 1.3)
- **No Celery setup** - comes in Phase 5
- **No Telegram bot** - comes in Phase 5
- **No production deployment** - only local + structure for cloud
- **No Kubernetes configs** - Docker Compose only for now

## 6. Design Considerations

### 6.1 Project Structure

```text
filterbets/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Pydantic Settings
│   │   └── database.py          # SQLAlchemy setup
│   ├── alembic/
│   │   ├── versions/            # Migration files
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_health.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .python-version
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   └── layout/
│   │   │       └── Header.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   └── NotFound.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── Makefile
└── README.md (updated)
```

### 6.2 Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://filterbets:filterbets@db:5432/filterbets
DATABASE_URL_SYNC=postgresql://filterbets:filterbets@db:5432/filterbets

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend
VITE_API_URL=http://localhost:8000
```

## 7. Technical Considerations

### 7.1 Dependencies

**Backend (Poetry):**

```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
asyncpg = "^0.30.0"
alembic = "^1.14.0"
pydantic-settings = "^2.6.0"
redis = "^5.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.28.0"
ruff = "^0.8.0"
mypy = "^1.13.0"
```

**Frontend (pnpm):**

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.28.0",
    "@tanstack/react-query": "^5.62.0",
    "axios": "^1.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^9.15.0",
    "prettier": "^3.4.0",
    "vitest": "^2.1.0",
    "@testing-library/react": "^16.0.0"
  }
}
```

### 7.2 Docker Considerations

- Use multi-stage builds to minimize image size
- Backend: `python:3.12-slim` base image
- Frontend: Build with Node, serve with `nginx:alpine`
- Use `.dockerignore` to exclude unnecessary files
- Health checks for all services

### 7.3 Database Connection

- Use async SQLAlchemy with `asyncpg` driver
- Connection pooling with sensible defaults (min=5, max=20)
- Separate sync URL for Alembic migrations

## 8. Success Metrics

| Metric | Target |
| -------- | -------- |
| `docker-compose up` starts all services | < 60 seconds |
| Backend health check passes | `GET /health` returns 200 |
| Frontend loads in browser | `localhost:5173` renders |
| All CI checks pass | Green pipeline on PR |
| Backend test coverage | > 80% for initial files |
| No linting errors | `ruff check` and `eslint` pass |
| No type errors | `mypy` and `tsc` pass |

## 9. Open Questions

| Question | Status | Notes |
| ---------- | -------- | ------- |
| Should we use pnpm or npm for frontend? | Decided: **pnpm** | Faster, better monorepo support |
| Python version: 3.11 or 3.12? | Decided: **3.12** | Latest stable, better performance |
| Include Jupyter notebook setup in Docker? | Deferred | Add in Phase 1.3 with data pipeline |
| Add pre-commit hooks now or later? | **Now** | Part of CI-ready setup |

---

*PRD Created: January 14, 2026*
*Feature: Project Scaffolding (Phase 1.1)*
*Estimated Effort: 2 weeks (production-ready)*
