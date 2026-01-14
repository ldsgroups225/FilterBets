# Tasks: Phase 2 - Core Backend API

## Relevant Files

### Database & Models

- `backend/app/models/__init__.py` - Models package init, exports all models
- `backend/app/models/user.py` - User model with password hashing
- `backend/app/models/league.py` - League model mapped from ESPN data
- `backend/app/models/team.py` - Team model with logo and venue info
- `backend/app/models/fixture.py` - Fixture model with scores and status
- `backend/app/models/team_stats.py` - Per-match team statistics model
- `backend/app/models/standing.py` - League standings model with form data
- `backend/app/models/filter.py` - User filter model with JSONB rules
- `backend/app/models/backtest_result.py` - Cached backtest results model

### Schemas (Pydantic)

- `backend/app/schemas/__init__.py` - Schemas package init
- `backend/app/schemas/user.py` - User request/response schemas
- `backend/app/schemas/auth.py` - Auth schemas (login, register, token)
- `backend/app/schemas/league.py` - League response schemas
- `backend/app/schemas/team.py` - Team response schemas with stats
- `backend/app/schemas/fixture.py` - Fixture response schemas
- `backend/app/schemas/filter.py` - Filter CRUD schemas with rules
- `backend/app/schemas/backtest.py` - Backtest request/response schemas
- `backend/app/schemas/common.py` - Shared schemas (pagination, errors)

### API Routes

- `backend/app/api/__init__.py` - API package init
- `backend/app/api/deps.py` - Dependency injection (get_db, get_current_user)
- `backend/app/api/v1/__init__.py` - V1 API router aggregation
- `backend/app/api/v1/auth.py` - Authentication endpoints
- `backend/app/api/v1/leagues.py` - Leagues endpoints
- `backend/app/api/v1/teams.py` - Teams endpoints with stats
- `backend/app/api/v1/fixtures.py` - Fixtures endpoints with filtering
- `backend/app/api/v1/filters.py` - Filter CRUD endpoints
- `backend/app/api/v1/backtest.py` - Backtest endpoints

### Services (Business Logic)

- `backend/app/services/__init__.py` - Services package init
- `backend/app/services/auth.py` - Authentication service (JWT, password)
- `backend/app/services/filter_engine.py` - Filter rule parser and matcher
- `backend/app/services/backtest.py` - Backtesting calculation service
- `backend/app/services/stats_calculator.py` - Team form and stats calculator

### Data Ingestion

- `backend/app/services/data_ingestion.py` - CSV to PostgreSQL ingestion service

### Utilities

- `backend/app/utils/__init__.py` - Utils package init
- `backend/app/utils/security.py` - Password hashing, JWT utilities
- `backend/app/utils/pagination.py` - Pagination helper utilities

### Tests

- `backend/tests/test_auth.py` - Authentication endpoint tests
- `backend/tests/test_leagues.py` - Leagues endpoint tests
- `backend/tests/test_teams.py` - Teams endpoint tests
- `backend/tests/test_fixtures.py` - Fixtures endpoint tests
- `backend/tests/test_filters.py` - Filter CRUD tests
- `backend/tests/test_backtest.py` - Backtest service tests
- `backend/tests/test_filter_engine.py` - Filter engine unit tests

### Migrations

- `backend/alembic/versions/` - Alembic migration files for new models

### Configuration

- `backend/app/main.py` - Update to include v1 API router
- `backend/app/config.py` - Add JWT settings

### Notes

- All API endpoints use `/api/v1/` prefix
- Tests use pytest with async support via pytest-asyncio
- Run tests with `cd backend && poetry run pytest tests/ -v`
- Run specific test file: `poetry run pytest tests/test_auth.py -v`
- Database migrations: `cd backend && poetry run alembic upgrade head`

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:

- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch `feature/phase2-core-api`

- [x] 1.0 Set up Database Models & Data Ingestion
  - [x] 1.1 Create `backend/app/models/__init__.py` package init
  - [x] 1.2 Create `backend/app/models/user.py` with User model (id, email, password_hash, created_at)
  - [x] 1.3 Create `backend/app/models/league.py` with League model mapped from `leagues.csv`
  - [x] 1.4 Create `backend/app/models/team.py` with Team model mapped from `teams.csv`
  - [x] 1.5 Create `backend/app/models/fixture.py` with Fixture model mapped from `fixtures.csv`
  - [x] 1.6 Create `backend/app/models/team_stats.py` with TeamStats model mapped from `teamStats.csv`
  - [x] 1.7 Create `backend/app/models/standing.py` with Standing model mapped from `standings.csv`
  - [x] 1.8 Create `backend/app/models/filter.py` with Filter model (user_id, name, rules JSONB, is_active)
  - [x] 1.9 Create `backend/app/models/backtest_result.py` with BacktestResult model
  - [x] 1.10 Update `backend/app/database.py` to import all models for Alembic detection
  - [x] 1.11 Create Alembic migration for all new models
  - [x] 1.12 Run migration to create tables: `alembic upgrade head`
  - [x] 1.13 Create `backend/app/services/data_ingestion.py` with CSV ingestion logic
  - [x] 1.14 Implement league ingestion from `data/base_data/leagues.csv`
  - [x] 1.15 Implement team ingestion from `data/base_data/teams.csv`
  - [x] 1.16 Implement fixture ingestion from `data/base_data/fixtures.csv`
  - [x] 1.17 Implement team_stats ingestion from `data/base_data/teamStats.csv`
  - [x] 1.18 Implement standings ingestion from `data/base_data/standings.csv`
  - [x] 1.19 Add database indexes for performance (fixtures.match_date, fixtures.league_id, team_stats.team_id)
  - [x] 1.20 Test data ingestion by running the service and verifying row counts

- [x] 2.0 Implement Authentication System
  - [x] 2.1 Add JWT dependencies to `backend/pyproject.toml` (python-jose, passlib[bcrypt])
  - [x] 2.2 Update `backend/app/config.py` with JWT settings (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE)
  - [x] 2.3 Create `backend/app/utils/security.py` with password hashing and JWT functions
  - [x] 2.4 Create `backend/app/schemas/auth.py` with UserCreate, UserLogin, Token, TokenData schemas
  - [x] 2.5 Create `backend/app/schemas/user.py` with UserResponse schema
  - [x] 2.6 Create `backend/app/services/auth.py` with authenticate_user, create_tokens functions
  - [x] 2.7 Create `backend/app/api/deps.py` with get_db and get_current_user dependencies
  - [x] 2.8 Create `backend/app/api/v1/__init__.py` with v1 router aggregation
  - [x] 2.9 Create `backend/app/api/v1/auth.py` with POST `/register` endpoint
  - [x] 2.10 Add POST `/login` endpoint returning JWT tokens
  - [x] 2.11 Add POST `/refresh` endpoint for token refresh
  - [x] 2.12 Add GET `/me` endpoint returning current user info
  - [x] 2.13 Update `backend/app/main.py` to include `/api/v1` router
  - [x] 2.14 Create `backend/tests/test_auth.py` with registration tests
  - [x] 2.15 Add login and token validation tests
  - [x] 2.16 Add protected endpoint access tests

- [x] 3.0 Build Leagues & Teams API
  - [x] 3.1 Create `backend/app/schemas/common.py` with PaginationMeta, PaginatedResponse schemas
  - [x] 3.2 Create `backend/app/utils/pagination.py` with paginate helper function
  - [x] 3.3 Create `backend/app/schemas/league.py` with LeagueResponse schema
  - [x] 3.4 Create `backend/app/api/v1/leagues.py` with GET `/leagues` endpoint (paginated)
  - [x] 3.5 Add GET `/leagues/{id}` endpoint for single league
  - [x] 3.6 Add GET `/leagues/{id}/teams` endpoint for teams in a league
  - [x] 3.7 Create `backend/app/schemas/team.py` with TeamResponse, TeamStatsResponse schemas
  - [x] 3.8 Create `backend/app/api/v1/teams.py` with GET `/teams/{id}` endpoint
  - [x] 3.9 Create `backend/app/services/stats_calculator.py` with form calculation logic
  - [x] 3.10 Add GET `/teams/{id}/stats` endpoint returning aggregated statistics
  - [x] 3.11 Add GET `/teams/{id}/form` endpoint returning last N games (default 5)
  - [x] 3.12 Add GET `/head-to-head/{team1_id}/{team2_id}` endpoint for H2H history
  - [x] 3.13 Create `backend/tests/test_leagues.py` with league endpoint tests
  - [x] 3.14 Create `backend/tests/test_teams.py` with team endpoint tests

- [x] 4.0 Build Fixtures API
  - [x] 4.1 Create `backend/app/schemas/fixture.py` with FixtureResponse, FixtureDetailResponse schemas
  - [x] 4.2 Create `backend/app/api/v1/fixtures.py` with GET `/fixtures` endpoint
  - [x] 4.3 Add query parameters: league_id, date_from, date_to, status, page, per_page
  - [x] 4.4 Add GET `/fixtures/today` endpoint for today's matches
  - [x] 4.5 Add GET `/fixtures/upcoming` endpoint for next 7 days
  - [x] 4.6 Add GET `/fixtures/{id}` endpoint with detailed fixture info and team stats
  - [x] 4.7 Implement fixture response to include home/away team details
  - [x] 4.8 Create `backend/tests/test_fixtures.py` with fixture endpoint tests
  - [x] 4.9 Add tests for filtering and pagination

- [x] 5.0 Implement Filter System
  - [x] 5.1 Create `backend/app/schemas/filter.py` with FilterCreate, FilterUpdate, FilterResponse schemas
  - [x] 5.2 Define FilterCondition schema with field, operator, value
  - [x] 5.3 Create `backend/app/api/v1/filters.py` with POST `/filters` endpoint
  - [x] 5.4 Add GET `/filters` endpoint listing user's filters
  - [x] 5.5 Add GET `/filters/{id}` endpoint (owner only)
  - [x] 5.6 Add PUT `/filters/{id}` endpoint for updates
  - [x] 5.7 Add DELETE `/filters/{id}` endpoint (soft delete)
  - [x] 5.8 Create `backend/app/services/filter_engine.py` with FilterEngine class
  - [x] 5.9 Implement rule parser supporting operators: =, !=, >, <, >=, <=, in, between
  - [x] 5.10 Implement filter matcher to find fixtures matching filter criteria
  - [x] 5.11 Add GET `/filters/{id}/matches` endpoint returning matching fixtures
  - [x] 5.12 Add filter validation (max 10 conditions, valid field names)
  - [x] 5.13 Create `backend/tests/test_filters.py` with filter CRUD tests
  - [x] 5.14 Create `backend/tests/test_filter_engine.py` with filter engine unit tests

- [x] 6.0 Implement Basic Backtesting Engine
  - [x] 6.1 Create `backend/app/schemas/backtest.py` with BacktestRequest, BacktestResponse schemas
  - [x] 6.2 Define bet_type enum: home_win, away_win, draw, over_2_5, under_2_5
  - [x] 6.3 Create `backend/app/services/backtest.py` with BacktestService class
  - [x] 6.4 Implement bet outcome evaluator (determine win/loss based on fixture result)
  - [x] 6.5 Implement profit calculator (flat stake ROI calculation)
  - [x] 6.6 Implement backtest runner that applies filter to historical fixtures
  - [x] 6.7 Calculate metrics: total_matches, wins, losses, win_rate, roi_percentage
  - [x] 6.8 Add POST `/filters/{id}/backtest` endpoint
  - [x] 6.9 Implement result caching in BacktestResult model (24h TTL)
  - [x] 6.10 Add Celery task for backtests exceeding 5s (optional, can defer)
  - [x] 6.11 Create `backend/tests/test_backtest.py` with backtest service tests

- [x] 7.0 Add API Documentation & Testing
  - [x] 7.1 Update FastAPI app metadata (title, description, version)
  - [x] 7.2 Add OpenAPI tags for endpoint grouping (auth, leagues, teams, fixtures, filters)
  - [x] 7.3 Add response model documentation to all endpoints
  - [x] 7.4 Verify Swagger UI at `/docs` shows all endpoints correctly
  - [x] 7.5 Run full test suite: `poetry run pytest tests/ -v --cov=app`
  - [x] 7.6 Ensure test coverage is above 80%
  - [x] 7.7 Run linting: `poetry run ruff check .`
  - [x] 7.8 Run type checking: `poetry run mypy app/`
  - [x] 7.9 Test all endpoints manually with sample requests
  - [x] 7.10 Commit all changes with message `feat: add Phase 2 core backend API`
