# FilterBets Tech Stack

## Architecture Overview

FilterBets uses a monorepo structure with clear separation between frontend, backend, and data components.

```text
FilterBets/
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── data/             # Data files and ingestion scripts
├── tasks/            # PRDs and task lists
└── agent-template/   # AI workflow templates
```

## Backend Stack

| Component | Technology | Version |
| ----------- | ------------ | --------- |
| Framework | FastAPI | Latest |
| Language | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0 |
| Migrations | Alembic | Latest |
| Task Queue | Celery + Celery Beat | 5.x |
| Cache/Broker | Redis | 5.x |

### Backend Commands

```bash
cd backend
poetry install                              # Install dependencies
poetry run uvicorn app.main:app --reload    # Run dev server
poetry run alembic upgrade head             # Run migrations
poetry run pytest tests/ -v                 # Run tests
poetry run ruff check .                     # Lint code
poetry run mypy app/                        # Type check
```

### Backend Structure

```text
backend/
├── app/
│   ├── api/v1/           # API route handlers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── tasks/            # Celery tasks
│   └── utils/            # Helpers
├── tests/                # Pytest tests
└── alembic/              # Database migrations
```

## Frontend Stack

| Component | Technology | Version |
| ----------- | ------------ | --------- |
| Framework | React | 18+ |
| Language | TypeScript | 5.x |
| Data Fetching | TanStack Query | v5 |
| Tables | TanStack Table | v8 |
| Styling | Tailwind CSS | 3.x |
| Components | shadcn/ui | Latest |
| Package Manager | pnpm | Latest |

### Frontend Commands

```bash
cd frontend
pnpm install          # Install dependencies
pnpm dev              # Run dev server
pnpm build            # Build for production
pnpm test             # Run tests
pnpm lint             # Lint code
pnpm typecheck        # Type check
```

## Database

| Component | Technology |
| ----------- | ------------ |
| Database | PostgreSQL 15+ |
| Port | 5433 (non-default) |
| Credentials | user=filterbets, password=filterbets, db=filterbets |

## Infrastructure

| Component | Technology |
| ----------- | ------------ |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Notifications | python-telegram-bot |

### Docker Commands

```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f backend    # View backend logs
```

## Development Tools

- **Linting (Python):** Ruff
- **Type Checking (Python):** MyPy
- **Testing (Python):** Pytest with pytest-asyncio
- **Linting (TypeScript):** ESLint
- **Formatting:** Prettier (frontend), Ruff (backend)

## Key Technical Decisions

1. **Async-first Backend:** All database operations use async SQLAlchemy
2. **JSONB for Filter Rules:** Flexible filter criteria storage in PostgreSQL
3. **Celery for Background Tasks:** Notifications, scheduled scans, backtesting
4. **JWT + OAuth2 Authentication:** Secure token-based auth
5. **Poetry for Python Dependencies:** Modern dependency management
