# Data Preparation Pipeline

This directory contains Jupyter notebooks for preparing ESPN Soccer data for backtesting.

## Overview

The pipeline transforms raw CSV data into clean, feature-engineered datasets optimized for filter backtesting.

## Key Enhancements (v2.0)

- **Optimized Performance**: Vectorized pandas operations, indexed merges, efficient memory usage
- **Schema Alignment**: Output matches `ingest_all_data.py` expected format for `features_metadata`
- **PRE-MATCH vs POST-MATCH**: Clear distinction to prevent look-ahead bias in filters
- **Relationship Efficiency**: Pre-computed lookups and indexed joins for large datasets
- **Comprehensive League Coverage**: 60+ leagues across all continents

### Notebooks

1. **01_data_exploration.ipynb** - Data profiling and quality assessment
   - Load all base_data CSVs
   - Analyze null values, foreign keys, date ranges
   - Comprehensive league tier classification
   - Generate data quality report

2. **02_data_cleaning.ipynb** - Data cleaning and validation
   - Filter to completed matches only
   - Optimized merges with team stats, teams, leagues
   - Apply league tier classification (Tier 1/2/3)
   - Handle missing values with proper strategy
   - Output: `matches_base.parquet`

3. **03_feature_engineering.ipynb** - Compute PRE-MATCH features for backtesting
   - Build team match history with vectorized operations
   - Compute rolling form (last 5/10 games) with shift(1) for point-in-time correctness
   - Compute rolling statistics (possession, shots, corners)
   - Compute home/away specific metrics
   - Compute head-to-head features (optimized for Tier 1/2)
   - Compute POST-MATCH outcome labels (ground truth)
   - Output: `matches_enriched.parquet`

4. **04_data_export.ipynb** - Final validation and export
   - Validate data quality and point-in-time correctness
   - Check for data leakage
   - Generate schema documentation with PRE/POST-MATCH classification
   - Export to Parquet and PostgreSQL-ready CSV
   - Output: `matches_final.parquet`, `matches_for_postgres.csv`

## League Tier Classification

### Tier 1 - Top 5 European Leagues (5 leagues)

| Code | League Name |
|------|-------------|
| ENG.1 | Premier League |
| ESP.1 | La Liga |
| ITA.1 | Serie A |
| GER.1 | Bundesliga |
| FRA.1 | Ligue 1 |

### Tier 2 - European Secondary (30+ leagues)

| Region | Leagues |
|--------|---------|
| **Second Divisions** | ENG.2-5, ESP.2, ITA.2, GER.2, FRA.2 |
| **Top European** | NED.1, POR.1, BEL.1, TUR.1, RUS.1, UKR.1, SCO.1, AUT.1, SUI.1, GRE.1, DEN.1, NOR.1, SWE.1, FIN.1, POL.1, CZE.1, CRO.1, SRB.1, ROM.1, BUL.1, HUN.1, CYP.1, ISR.1 |
| **European Cups** | UEFA.CHAMPIONS, UEFA.EUROPA, UEFA.EUROPA.CONF |

### Tier 2 - Americas (15+ leagues)

| Region | Leagues |
|--------|---------|
| **North America** | USA.1-2, MEX.1-2, CAN.1, CRC.1, CONCACAF.CHAMPIONS |
| **South America** | BRA.1-2, ARG.1-2, COL.1, CHI.1, PER.1, ECU.1, URU.1, PAR.1, VEN.1, BOL.1, CONMEBOL.LIBERTADORES, CONMEBOL.SUDAMERICANA |

### Tier 2 - Asia & Oceania (12+ leagues)

| Region | Leagues |
|--------|---------|
| **East Asia** | JPN.1-2, KOR.1, CHN.1 |
| **Middle East** | SAU.1, UAE.1, QAT.1 |
| **Southeast Asia** | THA.1, IDN.1, MYS.1, IND.1 |
| **Oceania** | AUS.1, AFC.CHAMPIONS |

### Tier 2 - Africa (10+ leagues)

| Region | Leagues |
|--------|---------|
| **North Africa** | EGY.1, MAR.1, TUN.1, ALG.1 |
| **West Africa** | NGA.1, GHA.1 |
| **East Africa** | KEN.1, UGA.1 |
| **Southern Africa** | RSA.1 |
| **Continental** | CAF.CHAMPIONS, CAF.CONFED |

### Tier 3 - Other Leagues

All remaining leagues (lower divisions, smaller competitions)

## Running the Pipeline

### Option 1: Using Poetry (Recommended)

```bash
# Install all dependencies (one-time)
poetry install

# Run notebooks using poetry environment
poetry run jupyter lab

# Open and run notebooks in order: 01 → 02 → 03 → 04
```

### Option 2: Using Python Script

```bash
# Run all notebooks
poetry run python run_pipeline.py all

# Run specific notebook
poetry run python run_pipeline.py 01  # or 02, 03, 04
```

### Option 3: Direct PostgreSQL Import

After running the pipeline:

```bash
# Import all data to PostgreSQL
poetry run python backend/scripts/ingest_all_data.py

# Or import only processed data (features)
poetry run python backend/scripts/ingest_all_data.py --step processed
```

## Output Files

After running the pipeline, the following files are created in `data/processed/`:

| File | Description |
| ------ | ------------- |
| `matches_base.parquet` | Cleaned matches with team stats (intermediate) |
| `matches_enriched.parquet` | Matches with all computed features |
| `matches_final.parquet` | Final backtesting dataset |
| `matches_for_postgres.csv` | PostgreSQL import ready (aligned with ingest_all_data.py) |
| `team_history.parquet` | Team match history with rolling features |
| `leagues_clean.parquet` | League metadata with tier classification |
| `schema_documentation.json` | Column definitions, stats, and PRE/POST-MATCH classification |
| `data_quality_report.json` | Data quality metrics |

## Data Schema

### Key Columns in matches_final.parquet

**Match Context:**

- `eventId`, `date`, `leagueId`, `league_code`, `league_name`, `tier`
- `homeTeamId`, `home_team_name`, `awayTeamId`, `away_team_name`

**Scores & Results (POST-MATCH - Ground Truth Only):**

- `homeTeamScore`, `awayTeamScore`
- `result` (H/D/A), `total_goals`
- `over_1_5`, `over_2_5`, `over_3_5`, `btts`
- `home_clean_sheet`, `away_clean_sheet`

**PRE-MATCH Features (Safe for Filter Conditions):**

| Feature Type | Columns |
|-------------|---------|
| Form (5 games) | `home_form_wins_5`, `home_form_draws_5`, `home_form_losses_5`, `home_form_points_5`, `home_form_goals_scored_5`, `home_form_goals_conceded_5`, `home_form_clean_sheets_5` |
| Form (10 games) | Same pattern with `_10` suffix |
| Rolling Stats | `home_possession_avg_5`, `home_shots_avg_5`, `home_corners_avg_5` |
| Home-Specific | `home_home_form_wins_5`, `home_home_form_goals_5` |
| Away-Specific | `away_away_form_wins_5`, `away_away_form_goals_5` |
| Head-to-Head | `h2h_matches`, `h2h_home_wins`, `h2h_away_wins`, `h2h_draws`, `h2h_avg_goals` |

**POST-MATCH Fields (Ground Truth - NOT for Filter Conditions):**

- `homeTeamScore`, `awayTeamScore`, `result`, `total_goals`
- `home_possessionPct`, `home_totalShots`, `home_shotsOnTarget`, `home_wonCorners`
- `away_possessionPct`, `away_totalShots`, `away_shotsOnTarget`, `away_wonCorners`

⚠️ **Important**: Using POST-MATCH fields in filter conditions causes **look-ahead bias** and will lead to unrealistic backtest results.

## Features Computed

### Team Form (Last N Games) - PRE-MATCH

- Wins, Draws, Losses count
- Points accumulated
- Goals scored/conceded average
- Clean sheets count
- Goal difference average

### Rolling Statistics (Last N Games) - PRE-MATCH

- Possession %
- Shots, Shots on Target
- Corners won
- Fouls committed

### Home/Away Specific - PRE-MATCH

- Home team form in home matches only
- Away team form in away matches only
- Venue-specific goal averages

### Head-to-Head - PRE-MATCH

- Total meetings (last 2 years)
- Win/Draw records from current home team perspective
- Average goals per meeting

### Match Outcomes (Ground Truth) - POST-MATCH

- Result: Home Win (H), Draw (D), Away Win (A)
- Total goals and Over/Under thresholds
- Both Teams to Score (BTTS)
- Clean sheets

## Data Quality

- **Completed Matches:** ~57,000+ (filtered from 67,000+ total)
- **Tier 1 Coverage:** ~99% have complete PRE-MATCH feature sets
- **Tier 2 Coverage:** ~95% have complete PRE-MATCH feature sets
- **Null Values:** <3% in critical PRE-MATCH columns after cleaning
- **Point-in-Time Correctness:** All PRE-MATCH features use only data available before each match (verified via shift(1))

## Schema Alignment with Backend

The output CSV (`matches_for_postgres.csv`) is aligned with `backend/scripts/ingest_all_data.py`:

```python
# Features stored in fixtures.features_metadata JSONB column:
features_metadata = {
    "total_goals": ...,
    "over_1_5": ..., "over_2_5": ..., "over_3_5": ...,
    "btts": ...,
    "home_clean_sheet": ..., "away_clean_sheet": ...,
    "home_possessionPct": ..., "home_totalShots": ..., "home_shotsOnTarget": ..., "home_wonCorners": ...,
    "away_possessionPct": ..., "away_totalShots": ..., "away_shotsOnTarget": ..., "away_wonCorners": ...,
    # Form features (5 and 10 games)
    "home_form_wins_5": ..., "home_form_points_5": ..., ...
    "away_form_wins_5": ..., "away_form_points_5": ..., ...
}
```

## Troubleshooting

**Issue:** Notebooks won't run

- Ensure dependencies are installed: `poetry install`
- Check Python version: 3.12+ required
- Verify pyarrow is installed: `poetry run python -c "import pyarrow; print(pyarrow.__version__)"`

**Issue:** Memory errors on large datasets

- Process notebooks one at a time
- Use chunked processing (see optimized notebooks)
- Close other applications to free up RAM

**Issue:** Missing data files

- Ensure `data/base_data/` contains all CSV files
- Run `data/download_data.py` to download from Kaggle
- Check that you have ~1.5GB of free disk space

**Issue:** pyarrow installation fails

- Update to Python 3.12+: pyarrow 16.1.0 requires Python 3.12+
- Try: `poetry lock && poetry install`
- Alternative: Use CSV format by changing `.to_parquet()` to `.to_csv()` in notebooks

## References

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Jupyter Documentation](https://jupyter.org/documentation)
- [FilterBets Backend - ingest_all_data.py](../backend/scripts/ingest_all_data.py)
- [Backtest Metrics Documentation](../docs/backtest-metrics.md)
