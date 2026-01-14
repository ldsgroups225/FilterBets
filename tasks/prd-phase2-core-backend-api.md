# PRD: Phase 2 - Core Backend API

## 1. Introduction/Overview

This PRD covers Phase 2 of the FilterBets implementation plan: building the Core Backend API. This phase establishes the foundational API layer that powers the entire application, including user authentication, match/team data endpoints, and the filter system for creating betting strategies.

**Problem Statement:** Users need a secure, performant API to access football match data, create custom filter strategies, and test those strategies against historical data. Without this API layer, the frontend cannot display data or allow users to interact with the platform.

**Goal:** Deliver a production-ready REST API with authentication, comprehensive football data endpoints, and a flexible filter system that enables users to create and validate betting strategies.

## 2. Goals

1. **Authentication:** Implement secure email/password authentication with JWT tokens
2. **Data Access:** Provide read endpoints for leagues, teams, fixtures, and statistics from the ESPN dataset
3. **Filter System:** Enable users to create, manage, and apply custom filter strategies using JSONB rules
4. **Basic Backtesting:** Allow users to test filter strategies against historical data with key metrics
5. **API Versioning:** Establish `/api/v1/` prefix for all endpoints from the start
6. **Performance:** API response times under 200ms (p95) for standard queries

## 3. User Stories

### Authentication

- **US-1:** As a new user, I want to register with my email and password so I can access the platform.
- **US-2:** As a registered user, I want to log in and receive a JWT token so I can access protected endpoints.
- **US-3:** As a logged-in user, I want to refresh my token before it expires so I stay authenticated.
- **US-4:** As a user, I want to view my profile information so I can verify my account details.

### Data Access

- **US-5:** As a user, I want to browse available leagues so I can focus on competitions I'm interested in.
- **US-6:** As a user, I want to view fixtures with filters (date, league, status) so I can find relevant matches.
- **US-7:** As a user, I want to see detailed fixture information including team stats so I can analyze matches.
- **US-8:** As a user, I want to view team statistics and recent form so I can assess team performance.
- **US-9:** As a user, I want to see head-to-head history between two teams so I can understand their rivalry.

### Filter System

- **US-10:** As a user, I want to create a filter with multiple criteria so I can define my betting strategy.
- **US-11:** As a user, I want to list and manage my saved filters so I can organize my strategies.
- **US-12:** As a user, I want to see which upcoming fixtures match my filter so I can identify betting opportunities.
- **US-13:** As a user, I want to run a backtest on my filter so I can validate its historical performance.

## 4. Functional Requirements

### 4.1 Authentication System

| ID | Requirement |
| ---- | ------------- |
| FR-1 | The system must allow users to register with email and password |
| FR-2 | Passwords must be hashed using bcrypt before storage |
| FR-3 | The system must validate email format and password strength (min 8 chars) |
| FR-4 | The system must issue JWT access tokens (15 min expiry) and refresh tokens (7 day expiry) |
| FR-5 | The system must provide a `/api/v1/auth/me` endpoint to retrieve current user info |
| FR-6 | The system must reject requests with invalid or expired tokens with 401 status |

### 4.2 Leagues API

| ID | Requirement |
| ---- | ------------- |
| FR-7 | `GET /api/v1/leagues` must return all available leagues with pagination |
| FR-8 | Each league must include: id, name, country/region, season info |
| FR-9 | `GET /api/v1/leagues/{id}/teams` must return teams in a specific league |

### 4.3 Fixtures API

| ID | Requirement |
| ---- | ------------- |
| FR-10 | `GET /api/v1/fixtures` must return fixtures with pagination (default 20 per page) |
| FR-11 | Fixtures must be filterable by: league_id, date_from, date_to, status |
| FR-12 | `GET /api/v1/fixtures/today` must return matches scheduled for today |
| FR-13 | `GET /api/v1/fixtures/upcoming` must return matches in the next 7 days |
| FR-14 | `GET /api/v1/fixtures/{id}` must return detailed fixture info including team stats |
| FR-15 | Fixture response must include: id, date, league, home_team, away_team, score, status |

### 4.4 Teams API

| ID | Requirement |
| ---- | ------------- |
| FR-16 | `GET /api/v1/teams/{id}` must return team details (name, logo, venue) |
| FR-17 | `GET /api/v1/teams/{id}/stats` must return aggregated team statistics |
| FR-18 | `GET /api/v1/teams/{id}/form` must return last N games (default 5) with results |
| FR-19 | `GET /api/v1/head-to-head/{team1_id}/{team2_id}` must return H2H history |

### 4.5 Filter System

| ID | Requirement |
| ---- | ------------- |
| FR-20 | `POST /api/v1/filters` must create a new filter with name and JSONB rules |
| FR-21 | `GET /api/v1/filters` must return all filters for the authenticated user |
| FR-22 | `GET /api/v1/filters/{id}` must return filter details (owner only) |
| FR-23 | `PUT /api/v1/filters/{id}` must update filter name, rules, or active status |
| FR-24 | `DELETE /api/v1/filters/{id}` must soft-delete the filter |
| FR-25 | `GET /api/v1/filters/{id}/matches` must return fixtures matching the filter criteria |
| FR-26 | Filter rules must support operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `between` |

### 4.6 Backtesting

| ID | Requirement |
| ---- | ------------- |
| FR-27 | `POST /api/v1/filters/{id}/backtest` must run backtest against historical data |
| FR-28 | Backtest request must accept: seasons (list), bet_type (home_win, away_win, draw, over_2_5, under_2_5) |
| FR-29 | Backtest response must include: total_matches, wins, losses, win_rate, roi_percentage |
| FR-30 | Backtests taking >5s must be queued as Celery tasks and return a job_id |

## 5. Non-Goals (Out of Scope)

- **OAuth/Social Login:** Only email/password auth in this phase
- **Telegram Integration:** Deferred to Phase 5
- **Real-time Odds:** Using historical data only; live odds API integration is Phase 3+
- **Advanced Backtest Analytics:** Streaks, monthly breakdown, drawdown analysis are Phase 3
- **Public/Shared Filters:** All filters are private in this phase
- **Rate Limiting:** Basic protection only; advanced rate limiting is future work
- **Player-level Statistics:** Focus on team-level stats; player data is Phase 3+

## 6. Design Considerations

### API Response Format

All API responses should follow this structure:

```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

Error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "field": "email" }
  }
}
```

### Filter Rules Schema

```json
{
  "bet_type": "home_win",
  "conditions": [
    {"field": "league_id", "operator": "in", "value": [3922, 3923]},
    {"field": "home_team_form_wins", "operator": ">=", "value": 3},
    {"field": "home_team_goals_avg", "operator": ">=", "value": 1.5}
  ]
}
```

### Supported Filter Criteria (Initial Set)

| Category | Field | Type | Description |
| ---------- | ------- | ------ | ------------- |
| Match | `league_id` | int[] | Filter by league(s) |
| Match | `match_date` | date range | Filter by date range |
| Form | `home_team_form_wins` | int | Home team wins in last 5 |
| Form | `away_team_form_wins` | int | Away team wins in last 5 |
| Form | `home_team_form_losses` | int | Home team losses in last 5 |
| Form | `away_team_form_losses` | int | Away team losses in last 5 |
| Stats | `home_team_goals_avg` | float | Home team avg goals scored |
| Stats | `away_team_goals_avg` | float | Away team avg goals scored |
| Stats | `home_team_conceded_avg` | float | Home team avg goals conceded |
| Stats | `away_team_conceded_avg` | float | Away team avg goals conceded |
| Standings | `home_team_position` | int | Home team league position |
| Standings | `away_team_position` | int | Away team league position |

## 7. Technical Considerations

### Database Models

New models required:

- `User` - User accounts with hashed passwords
- `Filter` - User-defined filter strategies with JSONB rules
- `BacktestResult` - Cached backtest results

Existing models from Phase 1 data ingestion:

- `League`, `Team`, `Fixture`, `TeamStats`, `Standing`

### Dependencies

- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `pydantic` - Request/response validation (already installed)

### Data Source

The ESPN Soccer dataset in `./data/base_data/` contains:

- `fixtures.csv` - 50,000+ matches with scores and status
- `leagues.csv` - 150+ leagues/competitions
- `teams.csv` - 5,000+ teams with logos
- `teamStats.csv` - Per-match team statistics (possession, shots, etc.)
- `standings.csv` - League tables with form data

### Performance Optimizations

- Add database indexes on: `fixtures(match_date)`, `fixtures(league_id)`, `team_stats(team_id)`
- Use Redis caching for frequently accessed data (league list, team details)
- Implement query result pagination with cursor-based pagination for large datasets

### Security

- All filter/backtest endpoints require authentication
- Users can only access their own filters
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM

## 8. Success Metrics

| Metric | Target |
| -------- | -------- |
| API response time (p95) | < 200ms |
| Authentication success rate | > 99% |
| Backtest execution time (1 season) | < 5s |
| Test coverage | > 80% |
| Zero critical security vulnerabilities | Pass |

## 9. Open Questions

1. **Backtest Bet Types:** Should we support BTTS (Both Teams To Score) in the initial release, or defer to Phase 3?
   - *Recommendation:* Include basic bet types (home_win, away_win, draw, over_2_5, under_2_5) now; BTTS in Phase 3

2. **Filter Complexity Limit:** Should we limit the number of conditions per filter?
   - *Recommendation:* Limit to 10 conditions per filter initially to prevent performance issues

3. **Historical Data Range:** How many seasons of data should backtesting support?
   - *Recommendation:* Support 2024 and 2025 data (available in dataset); older data requires additional ingestion

4. **Caching Strategy:** Should we cache backtest results, and for how long?
   - *Recommendation:* Cache for 24 hours, invalidate on filter update

---

*Document created: January 14, 2026*
*Phase: 2 of 6*
*Estimated Duration: 2 weeks*
