# FilterBets Implementation Plan

## Executive Summary

FilterBets is a football betting analytics platform inspired by BetMines. This plan outlines a phased approach to build a production-ready application with pre-match scanning, backtesting, and Telegram notifications.

**Current State:** Data pipeline foundation exists (Kaggle ESPN Soccer dataset downloaded with 11 CSV files covering fixtures, teams, players, leagues, venues, standings, and match statistics).

**Target:** Full-stack application with React frontend, FastAPI backend, PostgreSQL database, and Celery task queue.

---

## Phase 1: Foundation & Data Pipeline (Week 1-2)

### 1.1 Project Scaffolding

**Goal:** Set up the monorepo structure with all necessary configurations.

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create `backend/` directory with FastAPI boilerplate | High | 2h |
| Create `frontend/` directory with Vite + React + TypeScript | High | 2h |
| Create `notebooks/` directory for data exploration | Medium | 30m |
| Set up Docker Compose (PostgreSQL, Redis) | High | 2h |
| Configure `.env.example` with all required variables | High | 1h |
| Set up GitHub Actions CI/CD pipeline | Medium | 2h |

**Deliverables:**

```text
filterbets/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── notebooks/
├── docker-compose.yml
└── .env.example
```

### 1.2 Database Schema & Models

**Goal:** Design and implement the PostgreSQL schema based on the ESPN dataset + FilterBets requirements.

**Schema Mapping (ESPN CSV → PostgreSQL):**

| ESPN CSV | PostgreSQL Table | Notes |
| ---------- | ------------------ | ------- |
| `leagues.csv` | `leagues` | Add `is_active`, `country` |
| `teams.csv` | `teams` | Keep core fields |
| `venues.csv` | `venues` | Direct mapping |
| `players.csv` | `players` | Direct mapping |
| `fixtures.csv` | `fixtures` | Add `status` enum |
| `teamStats.csv` | `match_team_stats` | Per-match stats |
| `standings.csv` | `standings` | League tables |
| `teamRoster.csv` | `team_rosters` | Season rosters |

**New Tables (FilterBets-specific):**

| Table | Purpose |
| ------- | --------- |
| `users` | User accounts with Telegram integration |
| `filters` | User-defined filter strategies (JSONB rules) |
| `filter_matches` | Matches that triggered a filter |
| `backtest_results` | Historical backtest performance |
| `notifications` | Notification history |

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create SQLAlchemy models for ESPN data tables | High | 4h |
| Create SQLAlchemy models for FilterBets tables | High | 3h |
| Set up Alembic migrations | High | 1h |
| Create initial migration | High | 1h |
| Add database indexes for performance | Medium | 1h |

### 1.3 Data Ingestion Pipeline

**Goal:** Build automated ETL to load ESPN CSV data into PostgreSQL.

**Pipeline Steps:**

1. Read CSV files with Pandas
2. Clean & validate data (handle nulls, date formats)
3. Transform to match SQLAlchemy models
4. Bulk insert with conflict handling (upsert)

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create Jupyter notebook for data exploration | High | 3h |
| Build `data_ingestion.py` service | High | 6h |
| Implement CSV → DataFrame transformations | High | 4h |
| Implement DataFrame → PostgreSQL bulk insert | High | 3h |
| Add data validation & error handling | High | 2h |
| Create FastAPI endpoint `/data/ingest` | Medium | 1h |
| Write unit tests for ingestion | Medium | 2h |

**Data Validation Rules:**

- `fixtures.date` must be valid datetime
- `teamStats.possessionPct` must be 0-100
- Foreign keys must reference existing records
- No duplicate `eventId` in fixtures

---

## Phase 2: Core Backend API (Week 3-4)

### 2.1 Authentication System

**Goal:** Implement JWT-based authentication with Telegram linking.

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create `User` model with password hashing | High | 2h |
| Implement `/auth/register` endpoint | High | 2h |
| Implement `/auth/login` endpoint (JWT) | High | 2h |
| Implement `/auth/refresh` endpoint | High | 1h |
| Implement `/auth/me` endpoint | High | 1h |
| Create Telegram linking code generator | Medium | 2h |
| Implement `/auth/telegram/link` endpoint | Medium | 2h |
| Add OAuth2 dependency for protected routes | High | 1h |

**Security Considerations:**

- Use `bcrypt` for password hashing
- JWT expiry: 15 min access, 7 day refresh
- Rate limit login attempts
- Telegram codes expire after 10 minutes

### 2.2 Fixtures & Teams API

**Goal:** Build read endpoints for match and team data.

**Endpoints:**

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/leagues` | List all leagues |
| GET | `/leagues/{id}/teams` | Teams in a league |
| GET | `/fixtures` | List fixtures (paginated, filterable) |
| GET | `/fixtures/{id}` | Fixture details with stats |
| GET | `/fixtures/today` | Today's matches |
| GET | `/fixtures/upcoming` | Next 7 days |
| GET | `/teams/{id}` | Team details |
| GET | `/teams/{id}/stats` | Team statistics |
| GET | `/teams/{id}/form` | Last N games form |
| GET | `/head-to-head/{team1}/{team2}` | H2H history |

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create Pydantic schemas for responses | High | 3h |
| Implement fixtures router | High | 4h |
| Implement teams router | High | 3h |
| Implement leagues router | High | 2h |
| Add pagination utility | High | 1h |
| Add query filters (date, league, status) | High | 2h |
| Implement H2H endpoint | Medium | 2h |
| Write API tests | Medium | 3h |

### 2.3 Filter System

**Goal:** Allow users to create, manage, and apply filter strategies.

**Filter Rules Schema (JSONB):**

```json
{
  "bet_type": "home_win",
  "conditions": [
    {"field": "league_id", "operator": "in", "value": [1, 2, 3]},
    {"field": "home_team_form_wins", "operator": ">=", "value": 3},
    {"field": "home_odds", "operator": "between", "value": [1.5, 2.5]}
  ]
}
```

**Supported Filter Criteria:**

| Category | Fields |
| ---------- | -------- |
| Match Context | `league_id`, `match_date`, `home_team_id`, `away_team_id` |
| Team Form | `home_team_form_wins`, `away_team_form_losses`, `home_team_goals_avg` |
| Standings | `home_team_position`, `away_team_position`, `position_diff` |
| Match Stats | `home_possession_avg`, `away_shots_avg`, `corners_avg` |

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create `Filter` model with JSONB rules | High | 2h |
| Create Pydantic schemas for filter CRUD | High | 2h |
| Implement `/filters` CRUD endpoints | High | 4h |
| Build `FilterEngine` service | High | 6h |
| Implement filter rule parser | High | 4h |
| Implement filter matcher (fixtures → matches) | High | 4h |
| Add filter validation | Medium | 2h |
| Write filter engine tests | High | 3h |

---

## Phase 3: Backtesting Engine (Week 5-6)

### 3.1 Backtest Service

**Goal:** Test filter strategies against historical data.

**Algorithm:**

```python
def run_backtest(filter_id: int, seasons: list[str]) -> BacktestResult:
    filter = get_filter(filter_id)
    historical_fixtures = query_fixtures_by_seasons(seasons)
    matched_fixtures = apply_filter(filter.rules, historical_fixtures)
    
    results = []
    for fixture in matched_fixtures:
        outcome = evaluate_bet(fixture, filter.rules.bet_type)
        profit = calculate_profit(outcome, fixture.odds)
        results.append(BetResult(fixture, outcome, profit))
    
    return aggregate_results(results)
```

**Backtest Metrics:**

- Total matches
- Win/Loss/Push count
- Win rate (%)
- Total profit (flat stake)
- ROI percentage
- Average odds
- Longest winning/losing streak
- Monthly breakdown
- Drawdown analysis

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create `BacktestResult` model | High | 1h |
| Create Pydantic schemas for backtest | High | 1h |
| Implement `BacktestService` | High | 6h |
| Implement bet outcome evaluator | High | 3h |
| Implement profit calculator | High | 2h |
| Implement streak calculator | Medium | 2h |
| Implement monthly breakdown | Medium | 2h |
| Add Celery task for async backtests | High | 2h |
| Implement `/filters/{id}/backtest` endpoint | High | 2h |
| Write backtest tests | High | 3h |

### 3.2 Statistics Calculator

**Goal:** Pre-compute team statistics for efficient filtering.

**Computed Stats:**

- Last N games form (W-D-L)
- Goals scored/conceded average
- Home/Away specific records
- Clean sheets / Failed to score
- Points per game

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create `TeamSeasonStats` model | High | 2h |
| Implement `StatsCalculator` service | High | 4h |
| Implement form calculator (last N games) | High | 3h |
| Implement home/away split calculator | High | 2h |
| Add Celery task for stats refresh | Medium | 2h |
| Create materialized views for common queries | Medium | 2h |

---

## Phase 4: Frontend MVP (Week 7-8)

### 4.1 Project Setup

**Tech Stack:**

- React 18 + TypeScript
- Vite (build tool)
- TanStack Query (data fetching)
- TanStack Table (data tables)
- Tailwind CSS + shadcn/ui
- React Router v6

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Initialize Vite + React + TypeScript | High | 1h |
| Configure Tailwind CSS | High | 1h |
| Set up shadcn/ui components | High | 2h |
| Configure TanStack Query | High | 1h |
| Set up React Router | High | 1h |
| Create API client with axios | High | 2h |
| Set up authentication context | High | 2h |

### 4.2 Core Pages

**Pages:**

| Page | Route | Description |
| ------ | ------- | ------------- |
| Login | `/login` | User authentication |
| Register | `/register` | New user signup |
| Dashboard | `/` | Overview with today's matches |
| Fixtures | `/fixtures` | Match listing with filters |
| Fixture Detail | `/fixtures/:id` | Match details & stats |
| Teams | `/teams` | Team listing |
| Team Detail | `/teams/:id` | Team stats & form |
| Filters | `/filters` | User's filter strategies |
| Filter Builder | `/filters/new` | Create new filter |
| Filter Detail | `/filters/:id` | Filter details & backtest |
| Settings | `/settings` | User settings & Telegram |

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create layout components (Header, Sidebar) | High | 3h |
| Implement Login/Register pages | High | 4h |
| Implement Dashboard page | High | 4h |
| Implement Fixtures list page | High | 4h |
| Implement Fixture detail page | High | 3h |
| Implement Teams list page | Medium | 3h |
| Implement Team detail page | Medium | 3h |
| Implement Filters list page | High | 3h |
| Implement Filter builder page | High | 6h |
| Implement Filter detail + backtest page | High | 4h |
| Implement Settings page | Medium | 2h |

### 4.3 Filter Builder UI

**Goal:** Intuitive drag-and-drop filter creation.

**Components:**

- Criteria selector (dropdown by category)
- Operator selector (=, >, <, between, in)
- Value input (number, select, multi-select)
- Rule list with add/remove
- Preview of matching fixtures
- Backtest button with results display

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create FilterBuilder component | High | 4h |
| Create CriteriaSelector component | High | 2h |
| Create RuleRow component | High | 2h |
| Create BacktestResults component | High | 3h |
| Implement filter preview (live match count) | Medium | 2h |
| Add form validation | High | 2h |

---

## Phase 5: Notifications & Scanner (Week 9-10)

### 5.1 Celery Setup

**Goal:** Configure background task processing.

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Set up Celery with Redis broker | High | 2h |
| Configure Celery Beat scheduler | High | 2h |
| Create task for pre-match scanning | High | 3h |
| Create task for stats refresh | Medium | 2h |
| Create task for data ingestion | Medium | 2h |
| Add task monitoring (Flower) | Low | 1h |

### 5.2 Telegram Bot

**Goal:** Send notifications when filters match.

**Bot Commands:**

- `/start` - Welcome message
- `/link <code>` - Link Telegram to account
- `/status` - Check linked account
- `/filters` - List active filters
- `/help` - Show help

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create Telegram bot with BotFather | High | 30m |
| Implement bot handlers | High | 4h |
| Implement `/link` command | High | 2h |
| Create notification message templates | High | 2h |
| Implement `send_filter_alert` task | High | 3h |
| Add notification history tracking | Medium | 2h |
| Implement rate limiting | Medium | 2h |

### 5.3 Pre-Match Scanner

**Goal:** Automatically scan upcoming matches against active filters.

**Scanner Flow:**

1. Celery Beat triggers scanner at 8 AM and 2 PM
2. Fetch upcoming fixtures (next 24 hours)
3. For each user with active filters:
   - Apply filter rules to fixtures
   - For new matches, send Telegram notification
   - Record in `filter_matches` table

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Implement `PreMatchScanner` service | High | 4h |
| Create scanner Celery task | High | 2h |
| Configure Celery Beat schedule | High | 1h |
| Implement duplicate notification prevention | High | 2h |
| Add scanner status endpoint | Medium | 1h |
| Write scanner tests | Medium | 2h |

---

## Phase 6: Polish & Deployment (Week 11-12)

### 6.1 Testing & Quality

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Achieve 80% backend test coverage | High | 8h |
| Add frontend component tests | Medium | 4h |
| Add E2E tests with Playwright | Medium | 4h |
| Set up pre-commit hooks (ruff, mypy) | High | 1h |
| Configure GitHub Actions CI | High | 2h |

### 6.2 Documentation

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Write API documentation (OpenAPI) | High | 2h |
| Create SETUP.md with local dev instructions | High | 2h |
| Document filter criteria reference | Medium | 2h |
| Create user guide | Low | 2h |

### 6.3 Deployment

**Tasks:**

| Task | Priority | Effort |
| ------ | ---------- | -------- |
| Create production Docker Compose | High | 2h |
| Configure nginx reverse proxy | High | 2h |
| Set up SSL with Let's Encrypt | High | 1h |
| Configure environment variables | High | 1h |
| Set up database backups | High | 2h |
| Deploy to cloud (AWS/GCP/DO) | High | 4h |
| Configure monitoring (Sentry, logs) | Medium | 2h |

---

## Technical Decisions

### Why These Choices?

| Decision | Rationale |
| ---------- | ----------- |
| **FastAPI** | Async support, automatic OpenAPI docs, Pydantic validation |
| **SQLAlchemy 2.0** | Modern async support, type hints, mature ecosystem |
| **PostgreSQL** | JSONB for flexible filter rules, excellent performance |
| **Redis** | Dual-purpose: Celery broker + caching layer |
| **React + TanStack** | Industry standard, excellent DX, powerful data tables |
| **Tailwind + shadcn/ui** | Rapid UI development, consistent design system |
| **Celery** | Battle-tested task queue, perfect for scheduled jobs |
| **Docker Compose** | Reproducible dev environment, easy deployment |

### Database Indexes Strategy

```sql
-- High-priority indexes for common queries
CREATE INDEX idx_fixtures_date ON fixtures(match_date);
CREATE INDEX idx_fixtures_league_date ON fixtures(league_id, match_date);
CREATE INDEX idx_fixtures_status ON fixtures(status);
CREATE INDEX idx_team_stats_event_team ON match_team_stats(event_id, team_id);
CREATE INDEX idx_standings_league_season ON standings(league_id, season_type);
CREATE INDEX idx_filters_user_active ON filters(user_id) WHERE is_active = true;
CREATE INDEX idx_filter_matches_filter ON filter_matches(filter_id);
```

### Caching Strategy

| Data | TTL | Invalidation |
| ------ | ----- | -------------- |
| League list | 24h | Manual |
| Team details | 1h | On data refresh |
| Fixture list (today) | 5m | On status change |
| Team form stats | 1h | After match completion |
| Backtest results | 24h | On filter update |

---

## Risk Mitigation

| Risk | Mitigation |
| ------ | ------------ |
| **Data quality** | Validation layer, anomaly detection, manual review |
| **Backtest performance** | Celery async, query optimization, result caching |
| **Telegram rate limits** | Batch notifications, exponential backoff |
| **Filter complexity** | Limit conditions per filter, query timeout |
| **User trust** | Transparent backtest methodology, no guarantees |

---

## Success Metrics

### MVP Success Criteria

- [ ] User can register and login
- [ ] User can view fixtures and team stats
- [ ] User can create a filter with 3+ criteria
- [ ] User can run backtest and see results
- [ ] User can link Telegram and receive notifications
- [ ] Pre-match scanner runs twice daily

### Performance Targets

| Metric | Target |
| -------- | -------- |
| API response time (p95) | < 200ms |
| Backtest execution (1 season) | < 5s |
| Page load time | < 2s |
| Uptime | 99.5% |

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
| ------- | ---------- | ------------------ |
| Phase 1 | Week 1-2 | Project setup, DB schema, data pipeline |
| Phase 2 | Week 3-4 | Auth, Fixtures API, Filter system |
| Phase 3 | Week 5-6 | Backtesting engine, stats calculator |
| Phase 4 | Week 7-8 | Frontend MVP, filter builder UI |
| Phase 5 | Week 9-10 | Telegram bot, pre-match scanner |
| Phase 6 | Week 11-12 | Testing, docs, deployment |

**Total Estimated Duration:** 12 weeks

---

## Next Steps

1. **Validate this plan** - Review with stakeholders
2. **Set up development environment** - Docker, IDE, Git hooks
3. **Start Phase 1** - Project scaffolding and data pipeline
4. **Create PRD for Phase 1** - Use `agent-template/create-prd.md`

---

*Document created: January 14, 2026*
*Last updated: January 14, 2026*
