# PRD: FilterBets System Improvements

**Date:** 2026-01-16  
**Version:** 1.0  
**Status:** Ready for Implementation

---

## 1. Introduction

This document outlines a comprehensive set of improvements to the FilterBets football betting analytics platform. The current implementation has several issues affecting data quality, system reliability, and analytical accuracy that need to be addressed.

**Core Problems:**
1. **Look-Ahead Bias:** Current filters use post-match data (scores) instead of pre-match predictions
2. **Missing Odds Data:** Backtests use default odds (2.0) instead of actual historical odds
3. **Session Errors:** Greenlet errors when loading related entities in filter results
4. **Incomplete Data:** Premier League and other major leagues missing from database
5. **Security Gap:** MCP endpoints are unauthenticated
6. **Analytics Limitations:** Backtest results lack advanced metrics (Kelly Criterion, EV, statistical significance)
7. **Validation Gaps:** No pre-flight validation for filter parameters
8. **Unhealthy Services:** Celery worker and Telegram bot containers failing
9. **Documentation Gaps:** Known issues not documented
10. **Testing Gaps:** No integration tests for backtest/filter correlation

---

## 2. Goals

1. **Eliminate look-ahead bias** in all filter implementations
2. **Import historical odds data** for accurate ROI calculations
3. **Fix greenlet/session errors** in entity relationship loading
4. **Complete league data coverage** (Premier League, La Liga, Serie A, etc.)
5. **Add authentication** to MCP endpoints
6. **Enhance backtest metrics** with professional betting analytics
7. **Add filter validation** to prevent invalid or trivial filters
8. **Restore container health** for all services
9. **Document known issues** and workarounds
10. **Add integration tests** for core functionality

---

## 3. User Stories

### As a data analyst, I want:
- Accurate backtests with real odds so I can trust the ROI calculations
- Filters that use only pre-match data so results are realistic
- Statistical significance tests so I know which filters are genuinely predictive

### As a developer, I want:
- Greenlet errors fixed so filter matches endpoint works reliably
- Container health restored so the full stack runs correctly
- Integration tests so I can refactor with confidence

### As a user, I want:
- All major leagues (Premier League, La Liga, etc.) available so I can analyze my preferred competitions
- Clear validation messages so I know when my filters are poorly configured
- MCP endpoints secured so my data is protected

---

## 4. Functional Requirements

### 4.1 Fix Look-Ahead Bias (High Priority)

**REQ-1.1** The system must NOT allow filters to use post-match fields (`home_score`, `away_score`, `total_goals`, `home_team_winner`, etc.)

**REQ-1.2** The filter schema validation must reject any rule with a field that would not be available before the match

**REQ-1.3** The system must provide pre-match alternatives for all common filter use cases:
- `home_team_goals_avg` instead of `home_score >= X`
- `home_team_form_points_last5` instead of `home_team_winner`
- `total_expected_goals` (computed from averages) instead of `total_goals >= X`

**REQ-1.4** The system must display a warning when creating a filter with fields that have look-ahead bias potential

### 4.2 Import Odds Data (High Priority)

**REQ-2.1** The system must support importing odds from CSV/Parquet files

**REQ-2.2** The import script must handle common odds formats (decimal, fractional, American)

**REQ-2.3** The backtest service must use actual odds instead of default 2.0

**REQ-2.4** The backtest response must include:
- Average odds used
- Minimum/Maximum odds in dataset
- Odds distribution histogram (buckets)

### 4.3 Fix Greenlet/Session Errors (High Priority)

**REQ-3.1** The filter matches endpoint (`GET /filters/{id}/matches`) must not throw `MissingGreenlet` errors

**REQ-3.2** The system must use eager loading (selectinload) for all related entities in list queries

**REQ-3.3** All async queries must properly await session operations

### 4.4 Complete League Data (Medium Priority)

**REQ-4.1** The database must include at least one season of data for:
- Premier League (league_id: 39)
- La Liga (league_id: 140)
- Serie A (league_id: 135)
- Bundesliga (league_id: 78)

**REQ-4.2** The data import script must log missing leagues after import

**REQ-4.3** The fixtures API must filter correctly by league_id

### 4.5 MCP Authentication (Medium Priority)

**REQ-5.1** The MCP server must require authentication for all endpoints

**REQ-5.2** The authentication must use the same JWT mechanism as the REST API

**REQ-5.3** Unauthenticated MCP requests must return 401 with clear error message

**REQ-5.4** The MCP integration docs must document the authentication requirement

### 4.6 Enhanced Backtest Metrics (Medium Priority)

**REQ-6.1** The backtest response must include Kelly Criterion calculation

**REQ-6.2** The backtest response must include Expected Value (EV) per bet

**REQ-6.3** The backtest response must include 95% confidence interval for win rate

**REQ-6.4** The backtest response must include statistical significance (p-value) test

**REQ-6.5** The backtest response must include profit by month breakdown

### 4.7 Filter Validation (Medium Priority)

**REQ-7.1** Creating a filter must validate that at least 10 historical matches exist

**REQ-7.2** Creating a filter must warn if results exceed 5000 matches (too broad)

**REQ-7.3** Creating a filter must validate that field operators match expected value types

**REQ-7.4** The API must return clear error messages for validation failures

### 4.8 Container Health (Low Priority)

**REQ-8.1** All containers must report `healthy` status

**REQ-8.2** Celery worker must process backtest jobs successfully

**REQ-8.3** Telegram bot must connect and respond to commands

**REQ-8.4** Docker Compose healthchecks must be configured correctly

### 4.9 Documentation (Low Priority)

**REQ-9.1** The MCP integration docs must include known issues section

**REQ-9.2** The docs must list workarounds for fastapi-mcp 0.4.0 bugs

**REQ-9.3** The backtest docs must explain all metrics and formulas

### 4.10 Integration Tests (Low Priority)

**REQ-10.1** Tests must verify filter-to-outcome correlation exists

**REQ-10.2** Tests must verify backtest results are deterministic

**REQ-10.3** Tests must verify authentication works correctly

**REQ-10.4** Tests must achieve at least 80% coverage for core modules

---

## 5. Non-Goals

This PRD does NOT include:
- Real-time odds ingestion (out of scope)
- Machine learning predictions (future consideration)
- Telegram bot commands expansion (separate PRD)
- Frontend UI changes (separate effort)
- Performance optimization beyond fixing bugs
- Database migration from PostgreSQL to another system

---

## 6. Design Considerations

### 6.1 Filter Schema Validation

Add a new validation layer in `FilterCreate` schema:

```python
POST_MATCH_FIELDS = {
    "home_score", "away_score", "total_goals",
    "home_team_winner", "away_team_winner",
    "home_team_shootout_score", "away_team_shootout_score"
}

@field_validator("rules")
def validate_no_look_ahead_bias(cls, v):
    for rule in v:
        if rule.field in POST_MATCH_FIELDS:
            raise ValueError(
                f"Cannot use '{rule.field}' - this is post-match data. "
                "Use pre-match stats like 'home_team_goals_avg' instead."
            )
    return v
```

### 6.2 Odds Import Flow

```
data/processed/
├── matches_final.parquet    # Existing (no odds)
├── odds_final.parquet       # NEW: Historical odds
└── matches_with_odds.csv    # NEW: Combined dataset
```

### 6.3 Backtest Response Extension

```python
class EnhancedBacktestResponse(BaseModel):
    # Existing fields...
    kelly_fraction: float = Field(None, description="Kelly fraction (0.25 max)")
    expected_value: float = Field(None, description="Expected value per unit bet")
    win_rate_ci_lower: float = Field(None, description="95% CI lower bound")
    win_rate_ci_upper: float = Field(None, description="95% CI upper bound")
    p_value: float = Field(None, description="Statistical significance p-value")
    odds_stats: OddsStats = Field(None, description="Odds distribution")
```

---

## 7. Technical Considerations

### 7.1 Dependencies
- `fastapi-mcp` 0.4.0 has known lifespan issues (document workaround)
- SQLAlchemy 2.0 async requires proper session handling
- Statistical calculations require `scipy` or `numpy`

### 7.2 Database Schema Changes
- Add `odds_data` JSONB column to `fixtures` table (optional)
- Add `features_metadata` column already exists for computed stats

### 7.3 API Changes
- New endpoint: `GET /filters/validate` (pre-flight validation)
- Modified endpoint: `POST /filters/{id}/backtest` (enhanced response)
- New endpoint: `POST /odds/import` (admin only)

### 7.4 Migration Strategy
1. Create database migration for any schema changes
2. Add backward-compatible response fields
3. Deploy in order: database → backend → tests

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Filter look-ahead bias errors | 0 | Runtime validation |
| Backtest with real odds | 100% of matches | Odds coverage |
| Greenlet errors in logs | 0 | Log analysis |
| League coverage | Top 5 leagues present | Database query |
| MCP authenticated | 100% | Auth middleware |
| Backtest metrics completeness | All 6 new metrics | Response validation |
| Container health | All services healthy | Docker status |
| Test coverage | >= 80% | pytest coverage |

---

## 9. Implementation Plan

### Phase 1: Data Quality (Days 1-2)
- [ ] Add look-ahead bias validation to filter schema
- [ ] Create odds import script
- [ ] Import historical odds data
- [ ] Update backtest service to use real odds

### Phase 2: Bug Fixes (Days 3-4)
- [ ] Fix greenlet errors with eager loading
- [ ] Add pre-match filter field alternatives
- [ ] Fix container health issues
- [ ] Add Premier League data import

### Phase 3: Features (Days 5-7)
- [ ] Add MCP authentication
- [ ] Implement enhanced backtest metrics
- [ ] Add filter validation endpoint
- [ ] Create integration tests

### Phase 4: Documentation (Day 8)
- [ ] Document known issues
- [ ] Update API docs
- [ ] Write migration guide

---

## 10. Open Questions

1. **Odds Data Source:** Where should historical odds be sourced from? (Kaggle, API, manual upload?)
2. **Kelly Fraction Default:** Should we cap Kelly at 0.25 (fractional Kelly) by default?
3. **Statistical Test:** Which significance test is preferred? (Chi-square, binomial, or z-test?)
4. **Backward Compatibility:** Should we maintain old backtest response format with new fields optional?

---

## 11. Appendix

### A. Pre-Match vs Post-Match Fields

| Post-Match (NOT for filters) | Pre-Match Alternative |
|------------------------------|----------------------|
| home_score | home_team_goals_avg |
| away_score | away_team_goals_avg |
| total_goals | total_expected_goals |
| home_team_winner | home_team_form_points_last5 |
| home_team_clean_sheet | home_team_clean_sheet_pct |

### B. Enhanced Backtest Metrics Formulas

**Kelly Criterion:**
```
K% = (p * odds - (1 - p)) / (odds - 1)
Where p = win probability, odds = decimal odds
```

**Expected Value:**
```
EV = (win_probability * odds - 1)
```

**95% Confidence Interval:**
```
CI = win_rate ± 1.96 * sqrt(win_rate * (1 - win_rate) / n)
```
