# FilterBets Development Workflow

## AI-Assisted Development Process

Follow this structured workflow for all feature development and bug fixes.

## Phase 1: Define the Work

### Creating a PRD (Product Requirements Document)

Use the PRD template to define features clearly:

```text
Use #[[file:agent-template/create-prd.md]]

Feature: [Describe your feature in detail]
```

The PRD process:

1. AI asks 3-5 clarifying questions with lettered options
2. You respond with selections (e.g., "1A, 2C, 3B")
3. AI generates PRD saved to `/tasks/prd-[feature-name].md`

### Generating Tasks

Convert the PRD into actionable tasks:

```text
Use #[[file:agent-template/generate-tasks.md]] with the PRD

Create tasks from: tasks/prd-[feature-name].md
```

The task generation process:

1. AI creates high-level parent tasks (Task 0.0 is always "Create feature branch")
2. You confirm with "Go"
3. AI breaks down into sub-tasks saved to `/tasks/tasks-[feature-name].md`

## Phase 2: Implementation

### Working Through Tasks

Implement one sub-task at a time:

```text
Start on task 1.1 from tasks/tasks-[feature-name].md
```

After each task:

- AI implements the change
- **Test affected endpoints via MCP server at `/mcp`** (FastAPI-MCP auto-exposes all endpoints)
- You review the code
- Mark task complete by changing `- [ ]` to `- [x]`
- Move to next task

### Task Completion Checklist

For each task, ensure:

- [ ] Code follows project conventions
- [ ] Tests are written (if applicable)
- [ ] No linting errors
- [ ] Type hints are complete (Python) / Types defined (TypeScript)
- [ ] Endpoints tested via MCP server (`/mcp`)

## Phase 3: Verification

### Running the Workflow Orchestrator

After implementation, run quality checks:

```bash
# For new features
./git_workflow_orchestrator.py feat

# For bug fixes
./git_workflow_orchestrator.py bug

# For code review only (no changes)
./git_workflow_orchestrator.py review

# For data pipeline work
./git_workflow_orchestrator.py data
```

### What the Orchestrator Does

**feat/bug workflow:**

1. Git status check
2. Backend type checking (with fixes)
3. Backend linting (with fixes)
4. Frontend type checking (with fixes)
5. Frontend linting (with fixes)
6. Backend tests (with retries)
7. Frontend tests (with retries)
8. Final status check
9. Suggest commit message

**review workflow:**

- Same checks but read-only (no auto-fixes)

## Git Workflow

### Branch Naming

- Features: `feature/[feature-name]`
- Bug fixes: `fix/[bug-description]`
- Data work: `data/[description]`

### Commit Messages

Follow conventional commits:

- `feat: add filter backtesting endpoint`
- `fix: correct ROI calculation in backtest`
- `chore: update dependencies`
- `docs: add API documentation`
- `test: add filter engine tests`

## Quick Reference Commands

```bash
# Backend
cd backend && poetry run pytest tests/ -v          # Run tests
cd backend && poetry run ruff check . --fix        # Lint + fix
cd backend && poetry run alembic upgrade head      # Run migrations

# Frontend
cd frontend && pnpm test                           # Run tests
cd frontend && pnpm lint --fix                     # Lint + fix
cd frontend && pnpm typecheck                      # Type check

# Full stack
docker-compose up -d                               # Start services
docker-compose logs -f backend                     # View logs
```
