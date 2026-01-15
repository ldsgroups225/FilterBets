# DATA PREPARING TASKS

## Relevant Files

- `notebooks/01_data_exploration.ipynb` - Initial data profiling, quality assessment, and schema documentation
- `notebooks/02_data_cleaning.ipynb` - Data cleaning transformations and validation
- `notebooks/03_feature_engineering.ipynb` - Rolling averages, form metrics, H2H computation
- `notebooks/04_data_export.ipynb` - Final export to Parquet and PostgreSQL-ready formats
- `data/processed/matches_enriched.parquet` - Main backtesting dataset output
- `data/processed/team_season_stats.parquet` - Aggregated team statistics
- `data/processed/leagues_clean.parquet` - League metadata with tier classification
- `data/processed/h2h_history.parquet` - Head-to-head lookup table
- `data/processed/data_quality_report.json` - Data quality metrics and validation results
- `backend/app/services/data_loader.py` - Service to load processed data into PostgreSQL (future integration)

### Notes

- Notebooks should be executed in order (01 → 02 → 03 → 04)
- All intermediate outputs stored in `data/processed/` directory
- Use `poetry run jupyter lab` from project root to launch notebooks
- Parquet files require `pyarrow` package (already in dependencies)

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:

- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [ ] 0.0 Create feature branch
  - [ ] 0.1 Create and checkout a new branch: `git checkout -b data/preparation-pipeline`
  - [ ] 0.2 Create `notebooks/` directory if it doesn't exist
  - [ ] 0.3 Create `data/processed/` directory for output files

- [ ] 1.0 Data Exploration & Quality Assessment (01_data_exploration.ipynb)
  - [ ] 1.1 Create notebook with standard imports (pandas, numpy, pathlib, matplotlib, seaborn)
  - [ ] 1.2 Load all base_data CSVs and display shape, dtypes, and sample rows
  - [ ] 1.3 Document row counts: fixtures (67K), teamStats (103K), standings (6K), teams (4K), leagues (1K)
  - [ ] 1.4 Analyze null values percentage per column for each table
  - [ ] 1.5 Validate foreign key relationships (homeTeamId/awayTeamId → teams, leagueId → leagues)
  - [ ] 1.6 Analyze date range distribution in fixtures (2024-01 to 2026-10)
  - [ ] 1.7 Analyze match status distribution (56K completed, 9K scheduled)
  - [ ] 1.8 Identify Top 5 European leagues by leagueId (ENG.1=700, ESP.1=740, ITA.1=730, GER.1=720, FRA.1=710)
  - [ ] 1.9 Profile teamStats columns (32 metrics) and identify key statistics for filtering
  - [ ] 1.10 Generate and save data quality summary as JSON

- [ ] 2.0 Data Cleaning & Validation (02_data_cleaning.ipynb)
  - [ ] 2.1 Create notebook with cleaning functions
  - [ ] 2.2 Filter fixtures to completed matches only (statusId IN [28, 45, 46, 47, 51])
  - [ ] 2.3 Remove duplicate eventIds if any exist
  - [ ] 2.4 Standardize date column to UTC datetime format
  - [ ] 2.5 Create league tier classification (Tier 1: Top 5, Tier 2: Secondary European, Tier 3: Others)
  - [ ] 2.6 Merge fixtures with teams to get team names (home_team_name, away_team_name)
  - [ ] 2.7 Merge fixtures with leagues to get league_name and midsizeName
  - [ ] 2.8 Merge fixtures with teamStats (join on eventId + teamId for both home and away)
  - [ ] 2.9 Handle missing teamStats: fill numeric nulls with 0, document imputation
  - [ ] 2.10 Validate data integrity: no scores > 15, possession between 0-100%
  - [ ] 2.11 Create unified `matches_base` DataFrame with core columns
  - [ ] 2.12 Save intermediate `matches_base.parquet` to data/processed/

- [ ] 3.0 Feature Engineering - Team Form (03_feature_engineering.ipynb)
  - [ ] 3.1 Create notebook with feature engineering functions
  - [ ] 3.2 Sort matches by team and date for rolling calculations
  - [ ] 3.3 Implement `compute_team_form(team_id, before_date, n_games)` function
  - [ ] 3.4 Compute last 5 games form: wins, draws, losses, points, goals_scored, goals_conceded
  - [ ] 3.5 Compute last 10 games form: same metrics for longer-term trend
  - [ ] 3.6 Compute home-specific form (last 5 home games only)
  - [ ] 3.7 Compute away-specific form (last 5 away games only)
  - [ ] 3.8 Ensure point-in-time correctness: only use matches BEFORE current match date
  - [ ] 3.9 Add form features to matches DataFrame (home_form_*, away_form_*)

- [ ] 4.0 Feature Engineering - Team Statistics
  - [ ] 4.1 Implement `compute_rolling_stats(team_id, before_date, n_games)` function
  - [ ] 4.2 Compute rolling averages (last 5 games): possession, shots, shots_on_target, corners, fouls, cards
  - [ ] 4.3 Compute rolling averages (last 10 games): same metrics
  - [ ] 4.4 Compute home-specific rolling stats
  - [ ] 4.5 Compute away-specific rolling stats
  - [ ] 4.6 Add statistics features to matches DataFrame (home_possession_avg5, away_shots_avg5, etc.)

- [ ] 5.0 Feature Engineering - Standings Context
  - [ ] 5.1 Process standings data to get point-in-time league positions
  - [ ] 5.2 For each match, lookup home team's pre-match league position and points
  - [ ] 5.3 For each match, lookup away team's pre-match league position and points
  - [ ] 5.4 Compute position_difference (home_position - away_position)
  - [ ] 5.5 Handle missing standings (early season matches): use null or default values
  - [ ] 5.6 Add standings features to matches DataFrame

- [ ] 6.0 Feature Engineering - Head-to-Head
  - [ ] 6.1 Implement `compute_h2h(home_team_id, away_team_id, before_date)` function
  - [ ] 6.2 Find all previous meetings between the two teams (last 2 seasons)
  - [ ] 6.3 Compute H2H metrics: total_matches, home_wins, away_wins, draws
  - [ ] 6.4 Compute H2H average goals per match
  - [ ] 6.5 Get last meeting result
  - [ ] 6.6 Add H2H features to matches DataFrame
  - [ ] 6.7 Create separate h2h_history.parquet for lookup table

- [ ] 7.0 Feature Engineering - Match Outcomes (Ground Truth)
  - [ ] 7.1 Compute result column: 'H' (home win), 'D' (draw), 'A' (away win)
  - [ ] 7.2 Compute total_goals column
  - [ ] 7.3 Compute over/under flags: over_0_5, over_1_5, over_2_5, over_3_5
  - [ ] 7.4 Compute BTTS (both teams to score): True/False
  - [ ] 7.5 Compute clean_sheet flags: home_clean_sheet, away_clean_sheet
  - [ ] 7.6 Add all outcome columns to matches DataFrame

- [ ] 8.0 Data Export & Validation (04_data_export.ipynb)
  - [ ] 8.1 Create final export notebook
  - [ ] 8.2 Select and order final columns for matches_enriched
  - [ ] 8.3 Validate no future data leakage (spot check random matches)
  - [ ] 8.4 Generate final data quality report (null counts, coverage by league tier)
  - [ ] 8.5 Export `matches_enriched.parquet` to data/processed/
  - [ ] 8.6 Export `team_season_stats.parquet` with aggregated season stats
  - [ ] 8.7 Export `leagues_clean.parquet` with tier classification
  - [ ] 8.8 Export PostgreSQL-ready CSVs for database ingestion
  - [ ] 8.9 Print summary statistics: total matches, matches by tier, feature coverage
  - [ ] 8.10 Document final schema in notebook markdown

- [ ] 9.0 Integration & Documentation
  - [ ] 9.1 Update data/README.md with processed data documentation
  - [ ] 9.2 Add notebook execution instructions to README
  - [ ] 9.3 Verify all notebooks run end-to-end without errors
  - [ ] 9.4 Run `./git_workflow_orchestrator.py data` for validation
  - [ ] 9.5 Commit all notebooks and processed data schema documentation
