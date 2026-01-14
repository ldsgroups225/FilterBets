# Tasks: Phase 3 - Backtesting Engine & Statistics Calculator

## Relevant Files

### Database & Models

- `backend/app/models/team_computed_stats.py` - Pre-computed team statistics model
- `backend/app/models/backtest_job.py` - Async backtest job tracking model
- `backend/app/models/__init__.py` - Update to export new models
- `backend/alembic/versions/` - Migration for new tables

### Schemas (Pydantic)

- `backend/app/schemas/backtest.py` - Enhanced backtest schemas with analytics
- `backend/app/schemas/team_stats.py` - Computed stats response schemas
- `backend/app/schemas/backtest_job.py` - Job status schemas

### API Routes

- `backend/app/api/v1/backtest.py` - Backtest job management endpoints
- `backend/app/api/v1/teams.py` - Add computed stats endpoint
- `backend/app/api/v1/filters.py` - Update backtest endpoint for async

### Services (Business Logic)

- `backend/app/services/backtest.py` - Enhanced backtest with analytics
- `backend/app/services/stats_calculator.py` - Team statistics computation
- `backend/app/services/filter_engine.py` - Extended filter criteria support

### Celery Tasks

- `backend/app/tasks/__init__.py` - Tasks package init
- `backend/app/tasks/celery_app.py` - Celery configuration
- `backend/app/tasks/stats_tasks.py` - Stats refresh tasks
- `backend/app/tasks/backtest_tasks.py` - Async backtest tasks

### Tests

- `backend/tests/test_stats_calculator.py` - Stats calculator tests
- `backend/tests/test_backtest_analytics.py` - Enhanced backtest tests
- `backend/tests/test_backtest_jobs.py` - Async job tests

### Configuration

- `backend/app/config.py` - Add Celery/Redis settings
- `backend/pyproject.toml` - Add Celery dependency if needed

### Notes

- Run tests: `cd backend && poetry run pytest tests/ -v`
- Run Celery worker: `celery -A app.tasks.celery_app worker --loglevel=info`
- Run Celery beat: `celery -A app.tasks.celery_app beat --loglevel=info`

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, check it off by changing `- [ ]` to `- [x]`.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout branch `feature/phase3-backtesting-engine`

- [x] 1.0 Database Schema & Models
  - [x] 1.1 Create `backend/app/models/team_computed_stats.py` with TeamComputedStats model
  - [x] 1.2 Create `backend/app/models/backtest_job.py` with BacktestJob model
  - [x] 1.3 Update `backend/app/models/__init__.py` to export new models
  - [x] 1.4 Create Alembic migration for team_computed_stats table
  - [x] 1.5 Create Alembic migration for backtest_jobs table
  - [x] 1.6 Run migrations: `alembic upgrade head`
  - [x] 1.7 Add database indexes for performance

- [x] 2.0 Statistics Calculator Service
  - [x] 2.1 Create `backend/app/schemas/team_stats.py` with ComputedStatsResponse schema
  - [x] 2.2 Enhance `backend/app/services/stats_calculator.py` with full implementation
  - [x] 2.3 Implement `calculate_team_overall_stats()` method
  - [x] 2.4 Implement `calculate_team_home_stats()` method
  - [x] 2.5 Implement `calculate_team_away_stats()` method
  - [x] 2.6 Implement `calculate_team_form(n_games)` method for last N games
  - [x] 2.7 Implement `refresh_team_stats(team_id)` to update computed stats
  - [x] 2.8 Implement `refresh_all_team_stats()` for batch processing
  - [x] 2.9 Add `GET /teams/{id}/computed-stats` endpoint
  - [x] 2.10 Create `backend/tests/test_stats_calculator.py` with unit tests

- [ ] 3.0 Enhanced Backtest Analytics
  - [ ] 3.1 Update `backend/app/schemas/backtest.py` with BacktestAnalytics schema
  - [ ] 3.2 Add `calculate_streaks()` method to BacktestService
  - [ ] 3.3 Add `calculate_monthly_breakdown()` method to BacktestService
  - [ ] 3.4 Add `calculate_drawdown()` method to BacktestService
  - [ ] 3.5 Add `generate_profit_curve()` method to BacktestService
  - [ ] 3.6 Update `run_backtest()` to include analytics in response
  - [ ] 3.7 Create `backend/tests/test_backtest_analytics.py` with analytics tests

- [ ] 4.0 Extended Filter Criteria
  - [ ] 4.1 Update `backend/app/schemas/filter.py` allowed_fields with new criteria
  - [ ] 4.2 Update FilterEngine to join with team_computed_stats table
  - [ ] 4.3 Implement `_build_stats_condition()` for computed stats fields
  - [ ] 4.4 Add support for `home_team_form_wins_last5` filter
  - [ ] 4.5 Add support for `home_team_goals_avg` filter
  - [ ] 4.6 Add support for `away_team_goals_avg` filter
  - [ ] 4.7 Add support for `total_expected_goals` filter (computed field)
  - [ ] 4.8 Add support for `home_team_clean_sheet_pct` filter
  - [ ] 4.9 Update filter tests for new criteria

- [ ] 5.0 Celery Setup & Async Backtests
  - [ ] 5.1 Create `backend/app/tasks/__init__.py` package
  - [ ] 5.2 Create `backend/app/tasks/celery_app.py` with Celery configuration
  - [ ] 5.3 Update `backend/app/config.py` with Redis/Celery settings
  - [ ] 5.4 Create `backend/app/tasks/stats_tasks.py` with refresh_all_team_stats task
  - [ ] 5.5 Create `backend/app/tasks/backtest_tasks.py` with run_async_backtest task
  - [ ] 5.6 Configure Celery Beat schedule for daily stats refresh
  - [ ] 5.7 Create `backend/app/schemas/backtest_job.py` with job schemas
  - [ ] 5.8 Create `backend/app/api/v1/backtest.py` with job management endpoints
  - [ ] 5.9 Add `GET /backtest/jobs` endpoint to list user's jobs
  - [ ] 5.10 Add `GET /backtest/jobs/{job_id}` endpoint for job status
  - [ ] 5.11 Update `POST /filters/{id}/backtest` to support async parameter
  - [ ] 5.12 Create `backend/tests/test_backtest_jobs.py` with job tests

- [ ] 6.0 Integration & Testing
  - [ ] 6.1 Run full test suite: `poetry run pytest tests/ -v --cov=app`
  - [ ] 6.2 Ensure test coverage is above 80%
  - [ ] 6.3 Run linting: `poetry run ruff check .`
  - [ ] 6.4 Run type checking: `poetry run mypy app/`
  - [ ] 6.5 Test stats calculator with real data
  - [ ] 6.6 Test enhanced backtest with analytics
  - [ ] 6.7 Test async backtest job flow
  - [ ] 6.8 Update API documentation
  - [ ] 6.9 Commit changes: `feat: add Phase 3 backtesting engine & stats calculator`
