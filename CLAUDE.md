# CLAUDE.md - FilterBets AI Development Guide

This guide outlines the AI-assisted development workflow for the FilterBets project - a football betting analytics platform with AI-powered predictions, backtesting, and Telegram notifications.

## 1. Project Overview

FilterBets provides:

- **Pre-Match Scanner:** Automated match analysis with customizable filter strategies
- **Backtesting Engine:** Test strategies against historical data
- **Telegram Notifications:** Real-time alerts when matches meet filter criteria
- **Value Bet Detection:** AI-powered identification of betting opportunities

## 2. Tech Stack

| Layer | Technology |
| ------- | ------------ |
| Frontend | React 18+ / TypeScript / TanStack Query & Table / Tailwind CSS / shadcn/ui |
| Backend | FastAPI (Python 3.11+) / SQLAlchemy 2.0 / Alembic |
| Database | PostgreSQL 15+ |
| Cache/Broker | Redis |
| Task Queue | Celery + Celery Beat |
| Notifications | python-telegram-bot |
| Data Analysis | Jupyter / Pandas / NumPy |
| Auth | JWT + OAuth2 |
| DevOps | Docker / Docker Compose / GitHub Actions |

## 3. Core Project Commands

```bash
# Backend (FastAPI)
cd backend && pip install -r requirements.txt   # Install backend deps
uvicorn app.main:app --reload                   # Run backend dev server
alembic upgrade head                            # Run database migrations
celery -A tasks.celery_app worker --loglevel=info  # Run Celery worker
celery -A tasks.celery_app beat --loglevel=info    # Run Celery scheduler

# MCP Server (API Testing via LLM)
# FastAPI-MCP exposes all endpoints at /mcp for LLM integration
# Use this to test endpoints after completing tasks

# Frontend (React)
cd frontend && pnpm install                     # Install frontend deps
pnpm dev                                        # Run frontend dev server
pnpm build                                      # Build for production
pnpm test                                       # Run frontend tests

# Full Stack (Docker)
docker-compose up -d                            # Start all services
docker-compose down                             # Stop all services
docker-compose logs -f backend                  # View backend logs

# Data Pipeline
cd notebooks && jupyter lab                     # Launch Jupyter for data exploration
python -m tasks.data_ingestion                  # Run data import from Kaggle CSV

# Quality Checks
pnpm run lint                                   # Lint frontend
pnpm run typecheck                              # TypeScript check
ruff check backend/                             # Lint backend (Python)
mypy backend/                                   # Type check backend
pytest backend/tests/                           # Run backend tests
```

## 4. Project Conventions and Architecture

For detailed guidance on technology, code conventions, and architecture, refer to:

- `.kiro/steering/` - Project standards and norms
- `docs/DISCUTIONS.md` - Feature specifications, personas, and technical decisions

### Key Architecture Decisions

- **Monorepo Structure:** `backend/`, `frontend/`, `notebooks/`, `data/`
- **API Design:** RESTful endpoints organized by domain (`/auth`, `/fixtures`, `/filters`, `/scanner`)
- **Filter Rules:** Stored as JSONB in PostgreSQL for flexible querying
- **Background Tasks:** Celery handles notifications, scheduled scans, and data ingestion
- **Backtesting:** Runs as async Celery task for heavy computations

## 5. AI Development Workflows

### For Features (`feat`) or Bug Fixes (`bug`)

Follow this structured, three-phase process.

#### A. Define the Work (PRD & Task Generation)

1. **Create a PRD:** Use `agent-template/create-prd.md` to define the feature or bug fix.

    ```text
    Use @agent-template/create-prd.md

    Feature: [Describe your feature or the bug to be fixed in detail]
    ```

2. **Generate Tasks:** Use the new PRD and `agent-template/generate-tasks.md` to create a step-by-step plan.

    ```text
    Use @<your-prd-file>.md and @agent-template/generate-tasks.md to create the task list.
    ```

#### B. Implement the Tasks

- Instruct your AI assistant to implement the work, one sub-task at a time.
- **After each task:** Test affected endpoints via the MCP server at `/mcp` to verify functionality.

#### C. Verify and Finalize with the Orchestrator

- After implementation, run the automated script to format, test, and prepare your changes for commit.

    ```bash
    ./git_workflow_orchestrator.py feat  # Or `./git_workflow_orchestrator.py bug`
    ```

### For Code Reviews (`review`)

- To perform a read-only check of the current code, run the `review` agent.

    ```bash
    ./git_workflow_orchestrator.py review
    ```

### For Data Pipeline Work (`data`)

- For data ingestion, transformation, or Jupyter notebook work:

    ```bash
    ./git_workflow_orchestrator.py data
    ```

## 6. Key Domain Concepts

### Filter Criteria Categories

- **Match Context:** League, date range, team selection
- **Odds-Based:** Home/Draw/Away win odds, Over/Under, BTTS
- **Probability:** AI-calculated win/draw/goal probabilities
- **Team Form:** Last N games stats, league position, points
- **Home/Away Splits:** Specific home/away performance metrics
- **Head-to-Head:** Historical matchup data

### Core Entities

- `leagues` - Football leagues (Premier League, La Liga, etc.)
- `teams` - Teams with stats and league associations
- `fixtures` - Match data with scores and status
- `odds` - Bookmaker odds for each fixture
- `team_stats` - Aggregated team statistics per season
- `users` - User accounts with Telegram integration
- `filters` - User-defined filter strategies (rules as JSONB)
- `filter_matches` - Matches that triggered a filter
- `backtest_results` - Historical backtest performance data

## 7. Automated Workflow Configuration

*The block below is parsed by `git_workflow_orchestrator.py` and should not be modified unless you are changing the core workflow steps.*

<!--AGENT_WORKFLOWS_START-->
```yaml
agents:
  - name: review
    description: "Read-only workflow for code reviews. Runs checks without making changes."
    steps:
      - name: "Git Status Check"
        function: "check_git_status"
      - name: "Backend Type Checking (Read-only)"
        function: "run_backend_typecheck_readonly"
      - name: "Backend Linting (Read-only)"
        function: "run_backend_lint_readonly"
      - name: "Frontend Type Checking (Read-only)"
        function: "run_frontend_typecheck_readonly"
      - name: "Frontend Linting (Read-only)"
        function: "run_frontend_lint_readonly"
      - name: "Backend Testing (Read-only)"
        function: "run_backend_tests_readonly"
      - name: "Frontend Testing (Read-only)"
        function: "run_frontend_tests_readonly"

  - name: feat
    description: "Full workflow for new features. Fixes issues and suggests a commit."
    steps:
      - name: "Git Status Check"
        function: "check_git_status"
      - name: "Backend Type Checking"
        function: "run_backend_typecheck_fix"
      - name: "Backend Linting (with Fixes)"
        function: "run_backend_lint_fix"
      - name: "Frontend Type Checking"
        function: "run_frontend_typecheck_fix"
      - name: "Frontend Linting (with Fixes)"
        function: "run_frontend_lint_fix"
      - name: "Backend Testing (with Retries)"
        function: "run_backend_tests_with_retry"
      - name: "Frontend Testing (with Retries)"
        function: "run_frontend_tests_with_retry"
      - name: "Final Status Check"
        function: "check_final_status"
      - name: "Suggest Commit Message"
        function: "suggest_commit_message"

  - name: bug
    alias: fix
    description: "Full workflow for bug fixes. Fixes issues and suggests a commit."
    steps:
      - name: "Git Status Check"
        function: "check_git_status"
      - name: "Backend Type Checking"
        function: "run_backend_typecheck_fix"
      - name: "Backend Linting (with Fixes)"
        function: "run_backend_lint_fix"
      - name: "Frontend Type Checking"
        function: "run_frontend_typecheck_fix"
      - name: "Frontend Linting (with Fixes)"
        function: "run_frontend_lint_fix"
      - name: "Backend Testing (with Retries)"
        function: "run_backend_tests_with_retry"
      - name: "Frontend Testing (with Retries)"
        function: "run_frontend_tests_with_retry"
      - name: "Final Status Check"
        function: "check_final_status"
      - name: "Suggest Commit Message"
        function: "suggest_commit_message"

  - name: data
    description: "Workflow for data pipeline and notebook work."
    steps:
      - name: "Git Status Check"
        function: "check_git_status"
      - name: "Notebook Validation"
        function: "run_notebook_validation"
      - name: "Data Script Linting"
        function: "run_backend_lint_fix"
      - name: "Final Status Check"
        function: "check_final_status"
      - name: "Suggest Commit Message"
        function: "suggest_commit_message"
```
<!--AGENT_WORKFLOWS_END-->
