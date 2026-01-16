# Tasks: FilterBets System Improvements Implementation

**Based on PRD:** `prd-system-improvements.md`  
**Created:** 2026-01-16

## Relevant Files

### Backend Files (to be modified)
- `backend/app/schemas/filter.py` - Add look-ahead bias validation
- `backend/app/services/filter_engine.py` - Fix greenlet errors with eager loading
- `backend/app/api/v1/filters.py` - Add filter validation endpoint, fix matches
- `backend/app/services/backtest_service.py` - Add enhanced metrics
- `backend/app/schemas/backtest.py` - Add new metric fields
- `backend/app/main.py` - Add MCP authentication
- `backend/scripts/import_odds.py` - NEW: Odds import script
- `backend/scripts/import_premier_league.py` - NEW: PL data import
- `backend/scripts/check_data_counts.py` - Verify league coverage
- `backend/app/api/v1/backtest.py` - Update backtest response schema

### Test Files (to be created/modified)
- `backend/tests/test_filter_validation.py` - Test look-ahead bias detection
- `backend/tests/test_backtest_metrics.py` - Test enhanced metrics
- `backend/tests/test_filter_engine.py` - Fix greenlet tests
- `backend/tests/test_odds_import.py` - Test odds import

### Documentation Files
- `.kiro/steering/mcp-integration.md` - Add known issues section
- `docs/backtest-metrics.md` - NEW: Metrics documentation

### Docker/Infra
- `docker-compose.dev.yml` - Fix healthchecks if needed

---

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

---

## Tasks

### Phase 1: Data Quality (Days 1-2)

- [ ] 0.0 Create feature branch
  - [ ] 0.1 Create and checkout new branch `feature/system-improvements`

- [ ] 1.0 Fix Look-Ahead Bias
  - [ ] 1.1 Add POST_MATCH_FIELDS constant to filter.py
  - [ ] 1.2 Add look-ahead validation decorator
  - [ ] 1.3 Add pre-match field alternatives documentation
  - [ ] 1.4 Add user-facing warning messages
  - [ ] 1.5 Write unit tests for validation

- [ ] 2.0 Import Odds Data
  - [ ] 2.1 Create odds import script structure
  - [ ] 2.2 Add CSV/Parquet parsing for odds formats
  - [ ] 2.3 Update backtest service to use real odds
  - [ ] 2.4 Add odds statistics to response schema
  - [ ] 2.5 Write tests for odds import

### Phase 2: Bug Fixes (Days 3-4)

- [ ] 3.0 Fix Greenlet/Session Errors
  - [ ] 3.1 Add eager loading to filter_engine.py
  - [ ] 3.2 Fix session handling in filters.py
  - [ ] 3.3 Test filter matches endpoint

- [ ] 4.0 Fix Container Health
  - [ ] 4.1 Investigate celery-worker unhealthy status
  - [ ] 4.2 Investigate telegram-bot unhealthy status
  - [ ] 4.3 Fix any configuration issues
  - [ ] 4.4 Verify all services healthy

### Phase 3: Features (Days 5-7)

- [ ] 5.0 Add MCP Authentication
  - [ ] 5.1 Add auth dependency to MCP mount
  - [ ] 5.2 Update MCP integration docs
  - [ ] 5.3 Test authenticated MCP access

- [ ] 6.0 Enhanced Backtest Metrics
  - [ ] 6.1 Add Kelly Criterion calculation
  - [ ] 6.2 Add Expected Value calculation
  - [ ] 6.3 Add confidence intervals
  - [ ] 6.4 Add p-value significance test
  - [ ] 6.5 Update backtest response schema
  - [ ] 6.6 Write tests for new metrics

- [ ] 7.0 Add Filter Validation
  - [ ] 7.1 Create filter validation endpoint
  - [ ] 7.2 Add match count checks
  - [ ] 7.3 Add operator/type validation
  - [ ] 7.4 Write tests for validation

### Phase 4: Documentation & Data (Day 8)

- [ ] 8.0 Add Premier League Data
  - [ ] 8.1 Check data sources for PL data
  - [ ] 8.2 Create PL import script
  - [ ] 8.3 Import PL matches
  - [ ] 8.4 Verify league coverage

- [ ] 9.0 Update Documentation
  - [ ] 9.1 Add known issues to MCP docs
  - [ ] 9.2 Document backtest metrics and formulas
  - [ ] 9.3 Update README with current status

- [ ] 10.0 Integration Tests
  - [ ] 10.1 Test filter-to-outcome correlation
  - [ ] 10.2 Test backtest determinism
  - [ ] 10.3 Test authentication flows
  - [ ] 10.4 Achieve 80% coverage on core modules

---

## Progress Tracking

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1 | 0.0 - 2.5 | Pending |
| Phase 2 | 3.0 - 4.4 | Pending |
| Phase 3 | 5.0 - 7.4 | Pending |
| Phase 4 | 8.0 - 10.4 | Pending |

---

## Notes

- All new code must pass `ruff check` and `mypy` before committing
- Tests should use pytest with async support
- Document any workarounds for fastapi-mcp 0.4.0 issues
- Ensure backward compatibility where possible
