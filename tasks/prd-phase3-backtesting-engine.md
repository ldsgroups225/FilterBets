# PRD: Phase 3 - Backtesting Engine & Statistics Calculator

## 1. Introduction/Overview

This PRD covers Phase 3 of the FilterBets implementation: enhancing the backtesting engine with detailed analytics and building a statistics calculator for pre-computed team metrics.

**Problem Statement:** While Phase 2 delivered a basic backtesting capability (win rate, ROI, total profit), users need deeper insights to validate their betting strategies effectively. Additionally, the current filter system only supports basic fixture fields - users cannot filter by team form, league position, or historical performance metrics.

**Goal:** Deliver an enhanced backtesting engine with comprehensive analytics (streaks, monthly breakdown, drawdown) and a statistics calculator that pre-computes team metrics for efficient filtering and analysis.

## 2. Goals

1. **Enhanced Backtest Analytics:** Extend backtest results to include streak analysis, monthly performance breakdown, and drawdown metrics
2. **Statistics Calculator:** Build a service that computes and caches team statistics (form, goals averages, home/away splits)
3. **Extended Filter Criteria:** Enable filtering by computed team statistics (form wins, goals average, league position)
4. **Performance Optimization:** Pre-compute statistics to ensure fast filter matching and backtest execution
5. **Async Processing:** Support background task execution for heavy backtests via Celery

## 3. User Stories

### Backtest Analytics

- **US-1:** As a user, I want to see my strategy's longest winning and losing streaks so I can understand variance and risk.
- **US-2:** As a user, I want to see monthly performance breakdown so I can identify seasonal patterns in my strategy.
- **US-3:** As a user, I want to see maximum drawdown so I can understand the worst-case scenario for my bankroll.
- **US-4:** As a user, I want to export backtest results so I can analyze them in Excel or share with others.

### Statistics Calculator

- **US-5:** As a user, I want to filter matches by home team's recent form (e.g., "won 3+ of last 5") so I can find in-form teams.
- **US-6:** As a user, I want to filter by team's average goals scored so I can find high-scoring matchups.
- **US-7:** As a user, I want to filter by league position difference so I can find mismatches between top and bottom teams.
- **US-8:** As a user, I want team statistics to load quickly without waiting for calculations.

### Performance

- **US-9:** As a user, I want large backtests to run in the background so I don't have to wait on the page.
- **US-10:** As a user, I want to see backtest progress when running async so I know it's working.

## 4. Functional Requirements

### 4.1 Enhanced Backtest Analytics

| ID | Requirement |
| ---- | ------------- |
| FR-1 | Backtest results must include longest winning streak (consecutive wins) |
| FR-2 | Backtest results must include longest losing streak (consecutive losses) |
| FR-3 | Backtest results must include monthly breakdown (wins, losses, profit per month) |
| FR-4 | Backtest results must include maximum drawdown (largest peak-to-trough decline) |
| FR-5 | Backtest results must include profit chart data (cumulative profit over time) |
| FR-6 | Backtest results must be exportable as JSON |
| FR-7 | Backtests with >100 expected matches should run as Celery background tasks |
| FR-8 | Background backtests must return a job_id for status polling |
| FR-9 | `GET /backtest/{job_id}/status` must return job progress and results when complete |

### 4.2 Statistics Calculator Service

| ID | Requirement |
| ---- | ------------- |
| FR-10 | The system must calculate team form for last 5 games (wins, draws, losses, points) |
| FR-11 | The system must calculate team form for last 10 games |
| FR-12 | The system must calculate season-to-date statistics |
| FR-13 | Statistics must be split by home and away performance |
| FR-14 | The system must calculate average goals scored per game |
| FR-15 | The system must calculate average goals conceded per game |
| FR-16 | The system must calculate clean sheet count and percentage |
| FR-17 | The system must calculate "failed to score" count and percentage |
| FR-18 | Statistics must be pre-computed and stored in `team_computed_stats` table |
| FR-19 | Statistics must be refreshed daily via Celery Beat scheduled task |
| FR-20 | `GET /teams/{id}/computed-stats` must return all computed statistics |

### 4.3 Extended Filter Criteria

| ID | Requirement |
| ---- | ------------- |
| FR-21 | Filters must support `home_team_form_wins_last5` (0-5) |
| FR-22 | Filters must support `home_team_form_points_last5` (0-15) |
| FR-23 | Filters must support `away_team_form_wins_last5` (0-5) |
| FR-24 | Filters must support `home_team_goals_avg` (float) |
| FR-25 | Filters must support `away_team_goals_avg` (float) |
| FR-26 | Filters must support `home_team_conceded_avg` (float) |
| FR-27 | Filters must support `away_team_conceded_avg` (float) |
| FR-28 | Filters must support `home_team_clean_sheet_pct` (0-100) |
| FR-29 | Filters must support `total_expected_goals` (sum of both teams' averages) |
| FR-30 | Filter engine must join with computed stats table for these criteria |

### 4.4 API Endpoints

| ID | Requirement |
| ---- | ------------- |
| FR-31 | `POST /filters/{id}/backtest` must accept `async: boolean` parameter |
| FR-32 | `GET /backtest/jobs` must list user's pending/completed backtest jobs |
| FR-33 | `GET /backtest/jobs/{job_id}` must return job status and results |
| FR-34 | `DELETE /backtest/jobs/{job_id}` must cancel a pending job |
| FR-35 | `GET /teams/{id}/stats/form` must return form statistics |
| FR-36 | `POST /admin/stats/refresh` must trigger manual stats recalculation (admin only) |

## 5. Non-Goals (Out of Scope)

- **Real-time odds integration:** Using historical/static odds only
- **Player-level statistics:** Focus on team-level stats; player data is Phase 4+
- **Expected Goals (xG):** Advanced metric requiring additional data source
- **Live match statistics:** Only pre-match and historical data
- **Machine learning predictions:** AI-powered predictions are a future phase
- **Subscription/payment system:** Premium features gating is Phase 4

## 6. Design Considerations

### Backtest Response Schema (Enhanced)

```json
{
  "filter_id": 123,
  "bet_type": "home_win",
  "seasons": [2024, 2025],
  "total_matches": 156,
  "wins": 89,
  "losses": 67,
  "pushes": 0,
  "win_rate": 57.05,
  "total_profit": 12.45,
  "roi_percentage": 7.98,
  "avg_odds": 1.85,
  "analytics": {
    "longest_winning_streak": 8,
    "longest_losing_streak": 5,
    "max_drawdown": -15.50,
    "max_drawdown_pct": -12.3,
    "best_month": {"month": "2024-09", "profit": 8.20, "win_rate": 72.0},
    "worst_month": {"month": "2024-12", "profit": -4.50, "win_rate": 38.0},
    "monthly_breakdown": [
      {"month": "2024-08", "matches": 12, "wins": 7, "losses": 5, "profit": 2.10},
      {"month": "2024-09", "matches": 18, "wins": 13, "losses": 5, "profit": 8.20}
    ],
    "profit_curve": [
      {"match_index": 1, "cumulative_profit": 1.0},
      {"match_index": 2, "cumulative_profit": 2.0},
      {"match_index": 3, "cumulative_profit": 1.0}
    ]
  },
  "cached": false,
  "run_at": "2026-01-14T10:30:00Z"
}
```

### Team Computed Stats Schema

```json
{
  "team_id": 456,
  "season": 2024,
  "computed_at": "2026-01-14T08:00:00Z",
  "overall": {
    "matches_played": 20,
    "wins": 12,
    "draws": 4,
    "losses": 4,
    "goals_scored": 35,
    "goals_conceded": 18,
    "goals_scored_avg": 1.75,
    "goals_conceded_avg": 0.90,
    "clean_sheets": 8,
    "clean_sheet_pct": 40.0,
    "failed_to_score": 3,
    "failed_to_score_pct": 15.0,
    "points": 40,
    "points_per_game": 2.0
  },
  "home": {
    "matches_played": 10,
    "wins": 8,
    "draws": 1,
    "losses": 1,
    "goals_scored_avg": 2.10,
    "goals_conceded_avg": 0.60
  },
  "away": {
    "matches_played": 10,
    "wins": 4,
    "draws": 3,
    "losses": 3,
    "goals_scored_avg": 1.40,
    "goals_conceded_avg": 1.20
  },
  "form_last5": {
    "results": ["W", "W", "D", "W", "L"],
    "wins": 3,
    "draws": 1,
    "losses": 1,
    "points": 10,
    "goals_scored": 8,
    "goals_conceded": 4
  },
  "form_last10": {
    "results": ["W", "W", "D", "W", "L", "W", "W", "D", "L", "W"],
    "wins": 6,
    "draws": 2,
    "losses": 2,
    "points": 20
  }
}
```

### Extended Filter Criteria

| Category | Field | Type | Description |
| ---------- | ------- | ------ | ------------- |
| Form | `home_team_form_wins_last5` | int (0-5) | Home team wins in last 5 games |
| Form | `home_team_form_points_last5` | int (0-15) | Home team points in last 5 |
| Form | `away_team_form_wins_last5` | int (0-5) | Away team wins in last 5 |
| Form | `away_team_form_points_last5` | int (0-15) | Away team points in last 5 |
| Goals | `home_team_goals_avg` | float | Home team avg goals scored |
| Goals | `away_team_goals_avg` | float | Away team avg goals scored |
| Goals | `home_team_conceded_avg` | float | Home team avg goals conceded |
| Goals | `away_team_conceded_avg` | float | Away team avg goals conceded |
| Goals | `total_expected_goals` | float | Sum of both teams' scoring averages |
| Defense | `home_team_clean_sheet_pct` | float (0-100) | Home team clean sheet % |
| Defense | `away_team_clean_sheet_pct` | float (0-100) | Away team clean sheet % |
| Attack | `home_team_failed_to_score_pct` | float (0-100) | Home team FTS % |
| Attack | `away_team_failed_to_score_pct` | float (0-100) | Away team FTS % |

## 7. Technical Considerations

### Database Schema Changes

```sql
-- New table for pre-computed team statistics
CREATE TABLE team_computed_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(team_id),
    season_type INTEGER NOT NULL,
    
    -- Overall stats
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    goals_scored_avg DECIMAL(4,2) DEFAULT 0,
    goals_conceded_avg DECIMAL(4,2) DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    clean_sheet_pct DECIMAL(5,2) DEFAULT 0,
    failed_to_score INTEGER DEFAULT 0,
    failed_to_score_pct DECIMAL(5,2) DEFAULT 0,
    points INTEGER DEFAULT 0,
    points_per_game DECIMAL(4,2) DEFAULT 0,
    
    -- Home stats
    home_matches INTEGER DEFAULT 0,
    home_wins INTEGER DEFAULT 0,
    home_draws INTEGER DEFAULT 0,
    home_losses INTEGER DEFAULT 0,
    home_goals_scored_avg DECIMAL(4,2) DEFAULT 0,
    home_goals_conceded_avg DECIMAL(4,2) DEFAULT 0,
    
    -- Away stats
    away_matches INTEGER DEFAULT 0,
    away_wins INTEGER DEFAULT 0,
    away_draws INTEGER DEFAULT 0,
    away_losses INTEGER DEFAULT 0,
    away_goals_scored_avg DECIMAL(4,2) DEFAULT 0,
    away_goals_conceded_avg DECIMAL(4,2) DEFAULT 0,
    
    -- Form (last 5)
    form_last5_wins INTEGER DEFAULT 0,
    form_last5_draws INTEGER DEFAULT 0,
    form_last5_losses INTEGER DEFAULT 0,
    form_last5_points INTEGER DEFAULT 0,
    form_last5_goals_scored INTEGER DEFAULT 0,
    form_last5_goals_conceded INTEGER DEFAULT 0,
    
    -- Form (last 10)
    form_last10_wins INTEGER DEFAULT 0,
    form_last10_draws INTEGER DEFAULT 0,
    form_last10_losses INTEGER DEFAULT 0,
    form_last10_points INTEGER DEFAULT 0,
    
    computed_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(team_id, season_type)
);

CREATE INDEX idx_team_computed_stats_team ON team_computed_stats(team_id);
CREATE INDEX idx_team_computed_stats_season ON team_computed_stats(season_type);

-- Table for async backtest jobs
CREATE TABLE backtest_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    filter_id INTEGER NOT NULL REFERENCES filters(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    progress INTEGER DEFAULT 0, -- 0-100
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_backtest_jobs_user ON backtest_jobs(user_id);
CREATE INDEX idx_backtest_jobs_status ON backtest_jobs(status);
```

### Celery Tasks

```python
# tasks/stats.py
@shared_task
def refresh_team_stats(team_id: int = None):
    """Refresh computed stats for one or all teams"""
    pass

@shared_task
def refresh_all_team_stats():
    """Daily task to refresh all team statistics"""
    pass

# tasks/backtest.py
@shared_task(bind=True)
def run_async_backtest(self, job_id: str, filter_id: int, request_data: dict):
    """Run backtest as background task with progress updates"""
    pass
```

### Celery Beat Schedule

```python
beat_schedule = {
    'refresh-team-stats-daily': {
        'task': 'tasks.stats.refresh_all_team_stats',
        'schedule': crontab(hour=6, minute=0),  # 6 AM daily
    },
}
```

### Performance Considerations

- Pre-compute stats for all teams with fixtures in active seasons
- Use database indexes on team_id and season_type
- Cache backtest results for 24 hours (already implemented)
- Invalidate team stats cache when new fixtures are added
- Limit profit_curve data points to 500 for large backtests

### Dependencies

- Celery + Redis (already in stack, needs configuration)
- UUID for job IDs
- No new Python packages required

## 8. Success Metrics

| Metric | Target |
| -------- | -------- |
| Stats calculation time (all teams) | < 60 seconds |
| Filter with stats criteria response time | < 500ms |
| Backtest with analytics (100 matches) | < 3 seconds |
| Async backtest job completion | < 30 seconds |
| Team stats freshness | Updated daily by 7 AM |
| Test coverage for new code | > 80% |

## 9. Open Questions

1. **Stats history:** Should we store historical snapshots of team stats (e.g., what was their form on a specific date) for more accurate backtesting?
   - *Recommendation:* Defer to Phase 4 - use current stats for now

2. **League position:** Should we include league position in computed stats? Requires standings data integration.
   - *Recommendation:* Include if standings data is available in the dataset

3. **Backtest job retention:** How long should we keep completed backtest jobs?
   - *Recommendation:* 7 days, then auto-delete

4. **Rate limiting:** Should we limit how many async backtests a user can run concurrently?
   - *Recommendation:* Limit to 3 concurrent jobs per user

---

*Document created: January 14, 2026*
*Phase: 3 of 6*
*Estimated Duration: 2 weeks*
