# Data Preparation Pipeline

This directory contains Jupyter notebooks for preparing ESPN Soccer data for backtesting.

## Overview

The pipeline transforms raw CSV data into clean, feature-engineered datasets optimized for filter backtesting.

### Notebooks

1. **01_data_exploration.ipynb** - Data profiling and quality assessment
   - Load all base_data CSVs
   - Analyze null values, foreign keys, date ranges
   - Identify league tiers and key statistics
   - Generate data quality report

2. **02_data_cleaning.ipynb** - Data cleaning and validation
   - Filter to completed matches only
   - Merge fixtures with team stats, teams, leagues
   - Apply league tier classification
   - Handle missing values
   - Output: `matches_base.parquet`

3. **03_feature_engineering.ipynb** - Compute features for backtesting
   - Build team match history
   - Compute rolling form (last 5/10 games)
   - Compute rolling statistics (possession, shots, corners)
   - Compute home/away specific metrics
   - Compute head-to-head features
   - Compute match outcome labels (ground truth)
   - Output: `matches_enriched.parquet`

4. **04_data_export.ipynb** - Final validation and export
   - Validate data quality and point-in-time correctness
   - Generate schema documentation
   - Export to Parquet and PostgreSQL-ready CSV
   - Output: `matches_final.parquet`, `matches_for_postgres.csv`

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

### Option 3: Direct Python Execution

```bash
# Ensure dependencies are installed
poetry install

# Run notebooks manually by copying code cells into Python scripts
poetry run python your_script.py
```

## Output Files

After running the pipeline, the following files are created in `data/processed/`:

| File | Description |
| ------ | ------------- |
| `matches_base.parquet` | Cleaned matches with team stats (intermediate) |
| `matches_enriched.parquet` | Matches with all computed features |
| `matches_final.parquet` | Final backtesting dataset |
| `matches_for_postgres.csv` | PostgreSQL import ready |
| `team_history.parquet` | Team match history with rolling features |
| `leagues_clean.parquet` | League metadata with tier classification |
| `schema_documentation.json` | Column definitions and statistics |
| `data_quality_report.json` | Data quality metrics |

## Data Schema

### Key Columns in matches_final.parquet

**Match Context:**

- `eventId`, `date`, `leagueId`, `league_code`, `league_name`, `tier`
- `homeTeamId`, `home_team_name`, `awayTeamId`, `away_team_name`

**Scores & Results:**

- `homeTeamScore`, `awayTeamScore`
- `result` (H/D/A), `total_goals`
- `over_1_5`, `over_2_5`, `over_3_5`, `btts`
- `home_clean_sheet`, `away_clean_sheet`

**Pre-Match Features (Home Team):**

- `home_form_wins_5`, `home_form_draws_5`, `home_form_losses_5`, `home_form_pts_5`
- `home_form_goals_scored_5`, `home_form_goals_conceded_5`
- `home_possession_avg_5`, `home_shots_avg_5`, `home_corners_avg_5`
- `home_form_wins_10`, `home_form_goals_scored_10` (10-game variants)
- `home_home_form_wins_5`, `home_home_goals_5` (home-specific)

**Pre-Match Features (Away Team):**

- Same structure as home team with `away_` prefix

**Head-to-Head:**

- `h2h_matches`, `h2h_home_wins`, `h2h_away_wins`, `h2h_draws`, `h2h_avg_goals`

## Features Computed

### Team Form (Last N Games)

- Wins, Draws, Losses
- Points accumulated
- Goals scored/conceded average
- Clean sheets count

### Rolling Statistics (Last N Games)

- Possession %
- Shots, Shots on Target
- Corners won
- Fouls committed
- Yellow/Red cards

### Home/Away Specific

- Home team form in home matches
- Away team form in away matches
- Venue-specific goal averages

### Head-to-Head

- Total meetings (last 2 seasons)
- Win/Draw records
- Average goals per meeting

### Match Outcomes (Ground Truth)

- Result: Home Win (H), Draw (D), Away Win (A)
- Total goals and Over/Under thresholds
- Both Teams to Score (BTTS)
- Clean sheets

## Data Quality

- **Completed Matches:** ~57,000 (filtered from 67,353 total)
- **Tier 1 Coverage:** ~95% of matches have complete feature sets
- **Null Values:** <1% in critical columns after cleaning
- **Point-in-Time Correctness:** All features use only data available before each match

## Next Steps

1. Load `matches_final.parquet` into the backtesting engine
2. Use features to create filter strategies
3. Evaluate filter performance on historical data
4. Deploy filters to production scanner

## Troubleshooting

**Issue:** Notebooks won't run

- Ensure dependencies are installed: `poetry install`
- Check Python version: 3.12+ required
- Verify pyarrow is installed: `poetry run python -c "import pyarrow; print(pyarrow.__version__)"`

**Issue:** Memory errors on large datasets

- Process notebooks one at a time
- Reduce sample size in feature engineering notebook
- Close other applications to free up RAM

**Issue:** Missing data files

- Ensure `data/base_data/` contains all CSV files
- Run `data/download_data.py` to download from Kaggle
- Check that you have ~1.3GB of free disk space

**Issue:** pyarrow installation fails

- Update to Python 3.12+: pyarrow 16.1.0 requires Python 3.12+
- Try: `poetry lock && poetry install`
- Alternative: Use CSV format by changing `.to_parquet()` to `.to_csv()` in notebooks

## References

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Jupyter Documentation](https://jupyter.org/documentation)
- [FilterBets PRD](../tasks/prd-data-preparation-pipeline.md)
