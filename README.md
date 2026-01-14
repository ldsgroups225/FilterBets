# FilterBets

A football betting analytics platform with AI-powered predictions, backtesting, and Telegram notifications.

## Features

- **Pre-Match Scanner** - Automated match analysis with customizable filter strategies
- **Backtesting Engine** - Test strategies against historical data
- **Telegram Notifications** - Real-time alerts when matches meet filter criteria
- **Value Bet Detection** - AI-powered identification of betting opportunities

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 / TypeScript / TanStack Query / Tailwind CSS / shadcn/ui |
| Backend | FastAPI / SQLAlchemy 2.0 / Alembic |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Task Queue | Celery + Celery Beat |
| DevOps | Docker / Docker Compose / GitHub Actions |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ with Poetry
- Node.js 20+ with pnpm

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/filterbets.git
cd filterbets

# Copy environment variables
cp .env.example .env

# Start all services
make up

# View logs
make logs
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

```bash
# Install all dependencies
make install

# Run backend (in one terminal)
make dev-b

# Run frontend (in another terminal)
make dev-f
```

## Available Commands

```bash
# Docker
make up          # Start all services
make down        # Stop all services
make build       # Build Docker images
make logs        # View all logs

# Development
make install     # Install dependencies
make dev-b       # Run backend locally
make dev-f       # Run frontend locally

# Database
make migrate     # Run migrations
make makemigrations MSG="description"  # Create migration

# Quality
make test        # Run all tests
make lint        # Run all linters
make format      # Format code
make typecheck   # Type checking
```

## Project Structure

```
filterbets/
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   └── pages/     # Page components
│   └── public/        # Static assets
├── data/              # Data files (gitignored)
├── docs/              # Documentation
└── tasks/             # PRDs and task lists
```

## Development Workflow

1. Create a PRD using `agent-template/create-prd.md`
2. Generate tasks using `agent-template/generate-tasks.md`
3. Implement tasks step by step
4. Run `./git_workflow_orchestrator.py feat` to verify and commit

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
