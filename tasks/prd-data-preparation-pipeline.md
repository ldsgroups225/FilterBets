# PRD: Data Preparation Pipeline for Backtesting

## Introduction/Overview

FilterBets needs a robust data preparation pipeline to transform raw ESPN Soccer CSV data into clean, feature-rich datasets optimized for backtesting filter strategies. Currently, the raw data exists across 1,361 CSV files (1.3GB) but lacks the computed metrics, proper relationships, and cleaned format required for efficient backtesting.

This phase bridges the gap between raw data ingestion and the backtesting engine, ensuring users can test strategies against high-quality historical match data with meaningful statistical features.

## Goals

1. **Clean & Validate** - Remove duplicates, handle missing values, standardize formats, and validate data integrity across all source files
2. **Merge & Enrich** - Combine fixtures with team stats, standings, and key events into unified match records
3. **Compute Features** - Generate rolling averages, form metrics, home/away splits, and head-to-head statistics that power filter criteria
4. **Optimize for Queries** - Output data in formats optimized for both Jupyter analysis (Parquet) and PostgreSQL ingestion
5. **Document & Automate** - Create reproducible Jupyter notebooks with clear documentation for future data refreshes

## User Stories

1. **As a bettor (Chloe)**, I want historical matches to include pre-computed team form so I can create filters like "Home team won 3+ of last 5 games"
2. **As a data engineer (Alex)**, I want automated data validation so I can trust the backtest results are based on clean data
3. **As a power user (David)**, I want access to detailed match statistics (possession, shots, corners) so I can build advanced filter strategies
4. **As the backtesting engine**, I need fixtures with pre-match context (standings, form) computed at the time of each match, not current values

## Functional Requirements

### FR1: Data Loading & Exploration

1.1. Load all base_data CSVs (fixtures, teams, leagues, standings, teamStats, venues, status)
1.2. Load relevant league-specific data (keyEvents, lineups) for priority leagues
1.3. Generate data quality report (row counts, null percentages, date ranges, anomalies)
1.4. Document schema relationships and foreign key integrity

### FR2: Data Cleaning

2.1. Filter to completed matches only (statusId IN [28, 45, 46, 47, 51] = Full Time variants)
2.2. Remove duplicate eventIds
2.3. Standardize date formats to UTC datetime
2.4. Handle missing values:

- TeamStats: Fill numeric nulls with 0 or league averages where appropriate
- Standings: Forward-fill from last known position
2.5. Validate foreign keys (homeTeamId, awayTeamId exist in teams.csv)
2.6. Flag and exclude anomalous records (e.g., scores > 15, possession > 100%)

### FR3: League Prioritization

3.1. Tier 1 (Full processing): Top 5 European leagues

- ENG.1 (Premier League), ESP.1 (La Liga), ITA.1 (Serie A), GER.1 (Bundesliga), FRA.1 (Ligue 1)
3.2. Tier 2 (Standard processing): Secondary European + Major cups
- NED.1, POR.1, BEL.1, TUR.1, SCO.1, UEFA.CHAMPIONS, UEFA.EUROPA
3.3. Tier 3 (Basic processing): Other leagues as available
3.4. Create league metadata table with tier classification

### FR4: Feature Engineering - Team Form

4.1. Compute rolling form for each team before each match:

- Last 5 games: Wins, Draws, Losses, Points
- Last 5 games: Goals Scored, Goals Conceded, Clean Sheets
- Last 10 games: Same metrics for longer-term form
4.2. Compute home-specific form (last 5 home games)
4.3. Compute away-specific form (last 5 away games)
4.4. Form must be calculated using only matches BEFORE the current match date

### FR5: Feature Engineering - Team Statistics

5.1. Compute rolling averages per team (last 5 & 10 games):

- Possession %, Shots, Shots on Target, Shot Accuracy
- Corners Won, Fouls Committed
- Yellow Cards, Red Cards
- Pass Accuracy %
5.2. Compute home/away splits for all statistics
5.3. Aggregate at team-season level for season-to-date metrics

### FR6: Feature Engineering - Standings Context

6.1. For each match, capture pre-match standings:

- Home team league position, points, goal difference
- Away team league position, points, goal difference
- Position difference (home_position - away_position)
6.2. Standings must reflect state BEFORE the match was played

### FR7: Feature Engineering - Head-to-Head

7.1. For each fixture, compute H2H history:

- Total meetings (last 2 seasons)
- Home team wins, Away team wins, Draws
- Average goals in H2H matches
- Last meeting result
7.2. H2H computed only from matches before current fixture

### FR8: Feature Engineering - Match Outcomes

8.1. Compute match outcome labels for backtesting:

- Result: Home Win (1), Draw (X), Away Win (2)
- Total Goals: Over/Under 0.5, 1.5, 2.5, 3.5
- Both Teams to Score (BTTS): Yes/No
- Clean Sheet: Home, Away, Neither
- First Half result (if available from keyEvents)
8.2. These are the "ground truth" for backtest evaluation

### FR9: Data Output

9.1. Generate `matches_enriched.parquet` - Main backtesting dataset with all features
9.2. Generate `team_season_stats.parquet` - Aggregated team stats per season
9.3. Generate `leagues_clean.parquet` - League metadata with tiers
9.4. Generate `h2h_history.parquet` - Head-to-head lookup table
9.5. Create SQL-ready CSVs for PostgreSQL bulk import
9.6. Output data quality summary report

### FR10: Jupyter Notebooks

10.1. `01_data_exploration.ipynb` - Initial data profiling and quality assessment
10.2. `02_data_cleaning.ipynb` - Cleaning transformations with documentation
10.3. `03_feature_engineering.ipynb` - All computed features with explanations
10.4. `04_data_export.ipynb` - Final export and validation
10.5. All notebooks must be executable end-to-end with clear markdown documentation

## Non-Goals (Out of Scope)

- Real-time data updates or live match integration
- Odds data (not available in ESPN dataset - future enhancement)
- Player-level features for backtesting (focus on team-level)
- Expected Goals (xG) calculation (requires event coordinates not reliably available)
- Machine learning model training (separate phase)
- Commentary or play-by-play text analysis

## Design Considerations

### Data Flow

```text
Raw CSVs → Load & Validate → Clean → Merge → Feature Engineering → Export
   ↓              ↓            ↓        ↓              ↓              ↓
base_data/    Quality      Filtered  Unified      Rolling        Parquet +
+ events/     Report       Records   Matches      Metrics        PostgreSQL
```

### Key Technical Decisions

- **Parquet format** for intermediate and final outputs (columnar, compressed, fast)
- **Pandas + PyArrow** for data manipulation (standard, well-documented)
- **Point-in-time correctness** - All features computed using only data available before each match
- **Modular notebooks** - Each step isolated for debugging and rerunning

### Output Schema (matches_enriched)

```text
Match Context:
- event_id, match_date, league_id, league_name, season
- home_team_id, home_team_name, away_team_id, away_team_name
- venue_id, attendance

Match Result (Ground Truth):
- home_score, away_score, result (1/X/2)
- total_goals, over_1_5, over_2_5, over_3_5, btts

Pre-Match Home Team Features:
- home_form_w5, home_form_d5, home_form_l5, home_form_pts5
- home_goals_scored_avg5, home_goals_conceded_avg5
- home_possession_avg5, home_shots_avg5, home_corners_avg5
- home_league_position, home_league_points
- home_home_form_w5, home_home_goals_avg5 (home-specific)

Pre-Match Away Team Features:
- away_form_w5, away_form_d5, away_form_l5, away_form_pts5
- away_goals_scored_avg5, away_goals_conceded_avg5
- away_possession_avg5, away_shots_avg5, away_corners_avg5
- away_league_position, away_league_points
- away_away_form_w5, away_away_goals_avg5 (away-specific)

Head-to-Head:
- h2h_matches, h2h_home_wins, h2h_away_wins, h2h_draws
- h2h_avg_goals, h2h_last_result
```

## Technical Considerations

- **Memory management** - Process large files in chunks if needed (teamStats is 103K rows)
- **Date handling** - All dates in UTC, ensure timezone consistency
- **Null handling strategy** - Document all imputation decisions
- **Reproducibility** - Set random seeds, document pandas/numpy versions
- **Performance** - Use vectorized operations, avoid row-by-row iteration

## Success Metrics

1. **Data Quality**: <1% null values in critical columns after cleaning
2. **Coverage**: 95%+ of Tier 1 league matches have complete feature sets
3. **Accuracy**: 100% point-in-time correctness (no future data leakage)
4. **Performance**: Full pipeline runs in <10 minutes on standard hardware
5. **Usability**: Notebooks execute without errors, clear documentation

## Open Questions

1. Should we include cup competitions (FA Cup, Copa del Rey) in Tier 1 processing?
2. How far back should H2H history go? (Currently: 2 seasons)
3. Should we compute features for 3-game windows in addition to 5 and 10?
4. Priority for adding odds data from external sources in future iteration?

---

*Document created: January 15, 2026*
*Phase: 5.5 (Data Preparation - between Phase 5 and Phase 6)*
