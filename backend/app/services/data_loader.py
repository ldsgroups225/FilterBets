"""Service for loading processed data from Parquet files into the database."""

from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.team import Team


class DataLoaderService:
    """Service for loading processed Parquet data into PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"

    async def load_matches_from_parquet(self, limit: int | None = None) -> pd.DataFrame:
        """
        Load processed matches from Parquet file.

        Args:
            limit: Optional limit on number of rows to load

        Returns:
            DataFrame with enriched match data including features
        """
        parquet_path = self.data_dir / "matches_final.parquet"

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"Processed data not found at {parquet_path}. "
                "Run the data preparation notebooks first."
            )

        # Load parquet file
        df = pd.read_parquet(parquet_path)

        if limit:
            df = df.head(limit)

        return df

    async def sync_fixtures_to_db(self, batch_size: int = 1000) -> dict[str, int]:
        """
        Sync processed fixture data from Parquet to PostgreSQL.

        This updates existing fixtures with computed features or creates new ones.

        Args:
            batch_size: Number of records to process at once

        Returns:
            Dictionary with sync statistics
        """
        df = await self.load_matches_from_parquet()

        stats = {
            "total_rows": len(df),
            "updated": 0,
            "created": 0,
            "skipped": 0,
        }

        # Process in batches
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]
            await self._process_batch(batch, stats)
            await self.db.commit()

        return stats

    async def _process_batch(
        self, batch: pd.DataFrame, stats: dict[str, int]
    ) -> None:
        """Process a batch of fixtures."""
        for _, row in batch.iterrows():
            event_id = int(row["eventId"])

            # Check if fixture exists
            result = await self.db.execute(
                select(Fixture).where(Fixture.event_id == event_id)
            )
            fixture = result.scalar_one_or_none()

            if fixture:
                # Update existing fixture with features
                self._update_fixture_features(fixture, row)
                stats["updated"] += 1
            else:
                # Create new fixture
                fixture = await self._create_fixture_from_row(row)
                if fixture:
                    self.db.add(fixture)
                    stats["created"] += 1
                else:
                    stats["skipped"] += 1

    def _update_fixture_features(self, fixture: Fixture, row: pd.Series) -> None:
        """Update fixture with computed features from processed data."""
        # Update basic match info if missing
        if not fixture.home_team_score and pd.notna(row.get("homeTeamScore")):
            fixture.home_team_score = int(row["homeTeamScore"])
        if not fixture.away_team_score and pd.notna(row.get("awayTeamScore")):
            fixture.away_team_score = int(row["awayTeamScore"])

        # Store computed features in JSONB metadata field
        features = self._extract_features(row)
        if features:
            if not fixture.features_metadata:
                fixture.features_metadata = {}
            fixture.features_metadata["features"] = features

    async def _create_fixture_from_row(self, row: pd.Series) -> Fixture | None:
        """Create a new fixture from a DataFrame row."""
        try:
            # Verify teams exist
            home_team_id = int(row["homeTeamId"])
            away_team_id = int(row["awayTeamId"])

            home_team = await self.db.get(Team, home_team_id)
            away_team = await self.db.get(Team, away_team_id)

            if not home_team or not away_team:
                return None

            # Create fixture
            fixture = Fixture(
                event_id=int(row["eventId"]),
                league_id=int(row["leagueId"]),
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                home_team_score=int(row["homeTeamScore"]) if pd.notna(row.get("homeTeamScore")) else None,
                away_team_score=int(row["awayTeamScore"]) if pd.notna(row.get("awayTeamScore")) else None,
                match_date=pd.to_datetime(row["date"]),
                status_id=int(row.get("statusId", 28)),  # Default to Full Time
                features_metadata={"features": self._extract_features(row)},
            )

            return fixture

        except (KeyError, ValueError, TypeError):
            return None

    def _extract_features(self, row: pd.Series) -> dict[str, Any]:
        """Extract computed features from a row."""
        features: dict[str, Any] = {}

        # Form features (last 5 games)
        form_5_cols = [col for col in row.index if "form_" in col and "_5" in col]
        if form_5_cols:
            features["form_5"] = {
                col: float(row[col]) if pd.notna(row[col]) else None
                for col in form_5_cols
            }

        # Form features (last 10 games)
        form_10_cols = [col for col in row.index if "form_" in col and "_10" in col]
        if form_10_cols:
            features["form_10"] = {
                col: float(row[col]) if pd.notna(row[col]) else None
                for col in form_10_cols
            }

        # Rolling stats
        stats_cols = [col for col in row.index if "_avg_" in col]
        if stats_cols:
            features["rolling_stats"] = {
                col: float(row[col]) if pd.notna(row[col]) else None
                for col in stats_cols
            }

        # Match outcomes (ground truth)
        if "result" in row.index:
            features["outcome"] = {
                "result": str(row["result"]) if pd.notna(row.get("result")) else None,
                "total_goals": int(row["total_goals"]) if pd.notna(row.get("total_goals")) else None,
                "over_2_5": bool(row["over_2_5"]) if pd.notna(row.get("over_2_5")) else None,
                "btts": bool(row["btts"]) if pd.notna(row.get("btts")) else None,
            }

        # H2H features if available
        h2h_cols = [col for col in row.index if col.startswith("h2h_")]
        if h2h_cols:
            features["h2h"] = {
                col: float(row[col]) if pd.notna(row[col]) else None
                for col in h2h_cols
            }

        return features

    async def get_feature_coverage_stats(self) -> dict[str, Any]:
        """
        Get statistics about feature coverage in the processed data.

        Returns:
            Dictionary with coverage statistics
        """
        df = await self.load_matches_from_parquet()

        stats = {
            "total_matches": len(df),
            "date_range": {
                "min": str(df["date"].min()),
                "max": str(df["date"].max()),
            },
            "tier_distribution": df["tier"].value_counts().to_dict() if "tier" in df.columns else {},
            "feature_coverage": {},
        }

        # Check coverage of key features
        feature_groups = {
            "form_5": [col for col in df.columns if "form_" in col and "_5" in col],
            "form_10": [col for col in df.columns if "form_" in col and "_10" in col],
            "rolling_stats": [col for col in df.columns if "_avg_" in col],
            "outcomes": ["result", "total_goals", "over_2_5", "btts"],
        }

        for group_name, cols in feature_groups.items():
            available_cols = [col for col in cols if col in df.columns]
            if available_cols:
                # Calculate percentage of non-null values
                coverage = (df[available_cols].notna().sum().sum() / (len(df) * len(available_cols)) * 100)
                stats["feature_coverage"][group_name] = {  # type: ignore[assignment, index]
                    "columns": len(available_cols),
                    "coverage_pct": round(float(coverage), 2),
                }

        return stats

    async def load_team_history(self, team_id: int) -> pd.DataFrame | None:
        """
        Load team history from processed data.

        Args:
            team_id: Team ID to load history for

        Returns:
            DataFrame with team's match history and features
        """
        history_path = self.data_dir / "team_history.parquet"

        if not history_path.exists():
            return None

        df = pd.read_parquet(history_path)

        # Filter for specific team
        team_df = df[df["teamId"] == team_id].copy()

        return team_df if not team_df.empty else None

    async def export_features_for_ml(self, output_path: Path | None = None) -> Path:
        """
        Export features in ML-ready format (CSV with proper encoding).

        Args:
            output_path: Optional custom output path

        Returns:
            Path to exported file
        """
        df = await self.load_matches_from_parquet()

        if output_path is None:
            output_path = self.data_dir / "ml_features.csv"

        # Select feature columns
        feature_cols = [
            col for col in df.columns
            if any(x in col for x in ["form_", "_avg_", "h2h_", "result", "over_", "btts"])
        ]

        # Add identifiers
        id_cols = ["eventId", "date", "homeTeamId", "awayTeamId", "leagueId"]
        export_cols = [col for col in id_cols if col in df.columns] + feature_cols

        df[export_cols].to_csv(output_path, index=False)

        return output_path
