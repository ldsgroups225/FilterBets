# Data Integration Guide

## Overview

This guide explains how to integrate the processed match data (with computed features) into the FilterBets backtesting engine.

## Data Pipeline Flow

```text
Raw CSV Files → Data Ingestion → PostgreSQL (base tables)
                     ↓
              Jupyter Notebooks → Feature Engineering
                     ↓
         Processed Parquet/CSV → Import to PostgreSQL
                     ↓
              Backtesting Engine (with features)
```

## Step 1: Initial Data Ingestion (One-time)

Load raw CSV data into PostgreSQL:

```bash
# From project root
cd backend
poetry run python scripts/ingest_data.py
```

This creates the base tables:

- `venues` - Stadium information
- `leagues` - League metadata
- `teams` - Team information
- `fixtures` - Match results (without features)
- `team_stats` - Per-match team statistics
- `standings` - League table snapshots

## Step 2: Feature Engineering (Already Done ✅)

You've already run the Jupyter notebooks that:

1. Cleaned the data
2. Computed rolling form metrics (last 5/10 games)
3. Calculated rolling statistics (possession, shots, corners)
4. Generated home/away specific features
5. Created match outcome labels

**Output files in `data/processed/`:**

- `matches_final.parquet` - Main dataset with all features
- `matches_for_postgres.csv` - PostgreSQL-ready format
- `team_history.parquet` - Team match history
- `leagues_clean.parquet` - League metadata with tiers

## Step 3: Import Processed Data

Import the enriched data with features:

```bash
# From project root
cd backend
poetry run python scripts/import_processed_data.py
```

**Options:**

```bash
# Dry run (preview without committing)
poetry run python scripts/import_processed_data.py --dry-run

# Custom batch size
poetry run python scripts/import_processed_data.py --batch-size 500
```

**What this does:**

- Loads `data/processed/matches_for_postgres.csv`
- Updates existing fixtures with computed features
- Creates new fixtures if they don't exist
- Stores features in the `metadata` JSONB field

## Step 4: Using Features in Backtesting

### Current Approach (Basic)

The current `BacktestService` loads fixtures from PostgreSQL and evaluates bets based on scores:

```python
# backend/app/services/backtest.py
async def _get_historical_fixtures(self, rules, seasons):
    query = select(Fixture).where(
        Fixture.status_id == 28,  # Full Time
        Fixture.season_type.in_(seasons)
    )
    # Apply filter rules...
    return fixtures
```

### Enhanced Approach (With Features)

Access computed features from the `metadata` field:

```python
# Example: Filter by team form
def filter_by_form(fixture: Fixture) -> bool:
    """Check if home team has good recent form."""
    if not fixture.metadata or "features" not in fixture.metadata:
        return False
    
    features = fixture.metadata["features"]
    home_form_5 = features.get("home_form_5", {})
    
    # Home team won 3+ of last 5 games
    wins = home_form_5.get("wins", 0)
    return wins >= 3
```

### Feature Structure in metadata.features

```json
{
  "home_form_5": {
    "wins": 3.0,
    "draws": 1.0,
    "losses": 1.0,
    "points": 10.0,
    "goals_scored": 1.8,
    "goals_conceded": 0.8,
    "clean_sheets": 2.0
  },
  "home_form_10": { /* same structure */ },
  "away_form_5": { /* same structure */ },
  "away_form_10": { /* same structure */ },
  "home_rolling_stats": {
    "possession": 52.3,
    "shots": 14.2,
    "shots_on_target": 5.4,
    "corners": 6.8,
    "fouls": 11.2
  },
  "away_rolling_stats": { /* same structure */ },
  "outcomes": {
    "result": "H",
    "total_goals": 3,
    "over_2_5": true,
    "btts": true
  },
  "match_stats": {
    "home_possessionPct": 58.0,
    "home_totalShots": 16,
    "home_shotsOnTarget": 7,
    "home_wonCorners": 8
  }
}
```

## Step 5: Enhanced Backtesting Service

Create an enhanced service that uses features:

```python
# backend/app/services/enhanced_backtest.py
from app.services.backtest import BacktestService

class EnhancedBacktestService(BacktestService):
    """Backtesting with feature-based filtering."""
    
    async def run_backtest_with_features(
        self, 
        filter_obj: Filter, 
        request: BacktestRequest,
        feature_filters: dict | None = None
    ) -> BacktestResponse:
        """
        Run backtest with optional feature-based filtering.
        
        Args:
            filter_obj: Filter to backtest
            request: Backtest parameters
            feature_filters: Optional feature conditions
                Example: {
                    "home_form_5_wins": {"min": 3},
                    "away_form_5_losses": {"max": 1}
                }
        """
        # Get fixtures
        fixtures = await self._get_historical_fixtures(
            filter_obj.rules, request.seasons
        )
        
        # Apply feature filters
        if feature_filters:
            fixtures = self._filter_by_features(fixtures, feature_filters)
        
        # Evaluate bets
        results = self._evaluate_bets(fixtures, request.bet_type, request.stake)
        
        return self._calculate_metrics(filter_obj.id, request, results)
    
    def _filter_by_features(
        self, 
        fixtures: list[Fixture], 
        feature_filters: dict
    ) -> list[Fixture]:
        """Filter fixtures based on feature conditions."""
        filtered = []
        
        for fixture in fixtures:
            if not fixture.metadata or "features" not in fixture.metadata:
                continue
            
            features = fixture.metadata["features"]
            
            # Check all conditions
            if self._matches_feature_conditions(features, feature_filters):
                filtered.append(fixture)
        
        return filtered
    
    def _matches_feature_conditions(
        self, 
        features: dict, 
        conditions: dict
    ) -> bool:
        """Check if features match all conditions."""
        for key, condition in conditions.items():
            # Parse nested key (e.g., "home_form_5.wins")
            parts = key.split(".")
            value = features
            
            for part in parts:
                if part not in value:
                    return False
                value = value[part]
            
            # Check min/max conditions
            if "min" in condition and value < condition["min"]:
                return False
            if "max" in condition and value > condition["max"]:
                return False
        
        return True
```

## Step 6: API Endpoint Example

Add an endpoint to use feature-based backtesting:

```python
# backend/app/api/v1/backtest.py
from app.services.enhanced_backtest import EnhancedBacktestService

@router.post("/enhanced", response_model=BacktestResponse)
async def run_enhanced_backtest(
    filter_id: int,
    request: BacktestRequest,
    feature_filters: dict | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BacktestResponse:
    """Run backtest with feature-based filtering."""
    # Get filter
    filter_obj = await db.get(Filter, filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    # Run enhanced backtest
    service = EnhancedBacktestService(db)
    return await service.run_backtest_with_features(
        filter_obj, request, feature_filters
    )
```

## Step 7: Direct Parquet Access (Alternative)

For ML/analysis, load Parquet directly:

```python
# backend/app/services/data_loader.py (already created)
from app.services.data_loader import DataLoaderService

async def analyze_features():
    """Example: Load and analyze features."""
    service = DataLoaderService(db)
    
    # Load all matches with features
    df = await service.load_matches_from_parquet()
    
    # Filter by criteria
    tier1_matches = df[df["tier"] == 1]
    high_form_matches = df[df["home_form_wins_5"] >= 3]
    
    # Get statistics
    stats = await service.get_feature_coverage_stats()
    print(f"Feature coverage: {stats['feature_coverage']}")
```

## Verification

Check that features were imported successfully:

```bash
# Connect to PostgreSQL
psql -U filterbets -d filterbets

# Check fixtures with features
SELECT COUNT(*) FROM fixtures WHERE metadata ? 'features';

# View sample features
SELECT 
    event_id,
    home_team_id,
    away_team_id,
    metadata->'features'->'home_form_5' as home_form
FROM fixtures 
WHERE metadata ? 'features'
LIMIT 5;
```

## Performance Considerations

1. **JSONB Indexing**: Create GIN index for faster feature queries

   ```sql
   CREATE INDEX idx_fixtures_metadata_features 
   ON fixtures USING GIN ((metadata->'features'));
   ```

2. **Batch Processing**: Import uses 1000-record batches by default

3. **Memory**: Parquet files are loaded into memory - adjust batch size if needed

4. **Caching**: Backtest results are cached for 24 hours

## Troubleshooting

**Issue**: Import script can't find CSV file

```bash
# Check file exists
ls -lh data/processed/matches_for_postgres.csv

# Run notebooks if missing
poetry run python notebooks/run_pipeline.py all
```

**Issue**: Features not appearing in fixtures

```bash
# Check metadata field exists
psql -U filterbets -d filterbets -c "\d fixtures"

# Verify import ran successfully
poetry run python scripts/import_processed_data.py --dry-run
```

**Issue**: Slow backtest queries

```sql
-- Add index on metadata
CREATE INDEX idx_fixtures_metadata ON fixtures USING GIN (metadata);

-- Analyze table
ANALYZE fixtures;
```

## Next Steps

1. ✅ Import processed data: `poetry run python scripts/import_processed_data.py`
2. Create enhanced backtest service with feature filtering
3. Add API endpoints for feature-based backtesting
4. Update frontend to show feature-based filter options
5. Add feature importance analysis for ML models

## Summary

You now have two data sources:

- **PostgreSQL**: Base fixtures + features in `metadata` JSONB field
- **Parquet files**: Direct access for ML/analysis

The backtesting engine can use either approach:

- Query PostgreSQL for real-time filtering
- Load Parquet for batch analysis and ML training
