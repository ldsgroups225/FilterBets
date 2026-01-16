#!/usr/bin/env python3
"""
Import processed match data from Parquet/CSV into PostgreSQL with concurrent batch processing.

This script loads the enriched match data with computed features
from the data preparation pipeline into the FilterBets database.

Usage:
    poetry run python backend/scripts/import_processed_data.py [--dry-run] [--batch-size 500] [--max-workers 5]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd  # type: ignore
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team

settings = get_settings()


class DataImporter:
    """Import processed data into PostgreSQL with concurrent batch processing."""

    def __init__(self, db_url: str, max_workers: int = 5):
        # Create engine with pool settings optimized for concurrent operations
        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=max_workers + 2,  # Extra connections for overhead
            max_overflow=max_workers * 2,
            pool_pre_ping=True,
        )
        self.async_session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )  # type: ignore
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "processed"
        self.max_workers = max_workers

    async def import_from_csv(
        self, batch_size: int = 500, dry_run: bool = False
    ) -> dict[str, int]:
        """
        Import matches from CSV file with concurrent batch processing.

        Args:
            batch_size: Number of records per batch
            dry_run: If True, don't commit changes

        Returns:
            Dictionary with import statistics
        """
        csv_path = self.data_dir / "matches_for_postgres.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found at {csv_path}. "
                "Run the data preparation notebooks first."
            )

        print(f"📂 Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df):,} matches")
        print(f"⚙️  Using {self.max_workers} concurrent workers with batch size {batch_size}")

        stats = {
            "total_rows": len(df),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Split data into batches
        batches = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]
            batches.append((i, batch))

        print(f"📦 Created {len(batches)} batches")

        # Process batches concurrently
        semaphore = asyncio.Semaphore(self.max_workers)
        tasks = []

        async def process_with_semaphore(batch_idx, batch_data):
            async with semaphore:
                return await self._process_batch(batch_idx, batch_data, dry_run, len(df))

        for batch_idx, batch_data in batches:
            task = asyncio.create_task(process_with_semaphore(batch_idx, batch_data))
            tasks.append(task)

        # Wait for all tasks to complete and aggregate results
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in batch_results:
            if isinstance(result, BaseException):
                print(f"❌ Batch processing error: {result}")
                stats["errors"] += 1
            else:
                stats["created"] += result["created"]
                stats["updated"] += result["updated"]
                stats["skipped"] += result["skipped"]
                stats["errors"] += result["errors"]

        return stats

    async def _process_batch(
        self, batch_idx: int, batch: pd.DataFrame, dry_run: bool, total_rows: int
    ) -> dict[str, int]:
        """Process a batch of matches in a separate session."""
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
        batch_start = batch_idx
        batch_end = batch_idx + len(batch)

        try:
            async with self.async_session() as session:
                # Pre-load all teams and leagues needed for this batch to reduce queries
                team_ids = set(batch["homeTeamId"].dropna().astype(int).tolist() +
                             batch["awayTeamId"].dropna().astype(int).tolist())
                league_ids = set(batch["leagueId"].dropna().astype(int).tolist())

                # Fetch teams
                teams_result = await session.execute(
                    select(Team).where(Team.id.in_(team_ids))
                )
                teams = {team.id: team for team in teams_result.scalars().all()}

                # Fetch leagues
                leagues_result = await session.execute(
                    select(League).where(League.id.in_(league_ids))
                )
                leagues = {league.id: league for league in leagues_result.scalars().all()}

                # Fetch existing fixtures in this batch
                event_ids = batch["eventId"].dropna().astype(int).tolist()
                fixtures_result = await session.execute(
                    select(Fixture).where(Fixture.event_id.in_(event_ids))
                )
                existing_fixtures = {f.event_id: f for f in fixtures_result.scalars().all()}

                # Process each row
                for _, row in batch.iterrows():
                    try:
                        event_id = int(row["eventId"])

                        if event_id in existing_fixtures:
                            # Update existing fixture
                            fixture = existing_fixtures[event_id]
                            updated = self._update_fixture(fixture, row)
                            stats["updated" if updated else "skipped"] += 1
                        else:
                            # Create new fixture
                            fixture = self._create_fixture_from_cache(row, teams, leagues)
                            if fixture:
                                session.add(fixture)
                                stats["created"] += 1
                            else:
                                stats["skipped"] += 1
                    except Exception as e:
                        print(f"❌ Error processing eventId {row.get('eventId')}: {e}")
                        stats["errors"] += 1

                if not dry_run:
                    await session.commit()
                else:
                    await session.rollback()

                # Progress update
                progress = min(batch_end, total_rows)
                print(f"⏳ Batch {batch_start}-{batch_end}: Processed {progress:,}/{total_rows:,} ({progress/total_rows*100:.1f}%) | C:{stats['created']} U:{stats['updated']} S:{stats['skipped']} E:{stats['errors']}")

        except Exception as e:
            print(f"❌ Batch {batch_start}-{batch_end} failed: {e}")
            stats["errors"] += len(batch)

        return stats

    def _update_fixture(self, fixture: Fixture, row: pd.Series) -> bool:
        """
        Update fixture with features from processed data.

        Returns:
            True if updated, False if no changes
        """
        updated = False

        # Update scores if missing
        if fixture.home_team_score is None and pd.notna(row.get("homeTeamScore")):
            fixture.home_team_score = int(row["homeTeamScore"])
            updated = True

        if fixture.away_team_score is None and pd.notna(row.get("awayTeamScore")):
            fixture.away_team_score = int(row["awayTeamScore"])
            updated = True

        # Store features in features_metadata JSONB field
        features = self._extract_features(row)
        if features:
            if fixture.features_metadata is None:
                fixture.features_metadata = {}
            fixture.features_metadata["features"] = features
            updated = True

        return updated

    def _create_fixture_from_cache(
        self, row: pd.Series, teams: dict, leagues: dict
    ) -> Fixture | None:
        """Create new fixture from row using cached teams/leagues."""
        try:
            # Verify required fields
            event_id = int(row["eventId"])
            league_id = int(row["leagueId"])
            home_team_id = int(row["homeTeamId"])
            away_team_id = int(row["awayTeamId"])

            # Verify teams and league exist in cache
            if home_team_id not in teams or away_team_id not in teams:
                return None
            if league_id not in leagues:
                return None

            # Create fixture
            fixture = Fixture(
                event_id=event_id,
                league_id=league_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                home_team_score=int(row["homeTeamScore"]) if pd.notna(row.get("homeTeamScore")) else None,
                away_team_score=int(row["awayTeamScore"]) if pd.notna(row.get("awayTeamScore")) else None,
                match_date=pd.to_datetime(row["date"]),
                status_id=28,  # Full Time
                season_type=2024,  # Default season
                features_metadata={"features": self._extract_features(row)},
            )

            return fixture

        except (KeyError, ValueError, TypeError):
            return None

    def _extract_features(self, row: pd.Series) -> dict:
        """Extract all computed features from row."""
        features = {}

        # Home team form (5 games)
        home_form_5 = {}
        for col in ["wins", "draws", "losses", "points", "goals_scored", "goals_conceded", "clean_sheets"]:
            key = f"home_form_{col}_5"
            if key in row.index and pd.notna(row[key]):
                home_form_5[col] = float(row[key])
        if home_form_5:
            features["home_form_5"] = home_form_5

        # Home team form (10 games)
        home_form_10 = {}
        for col in ["wins", "draws", "losses", "points", "goals_scored", "goals_conceded", "clean_sheets"]:
            key = f"home_form_{col}_10"
            if key in row.index and pd.notna(row[key]):
                home_form_10[col] = float(row[key])
        if home_form_10:
            features["home_form_10"] = home_form_10

        # Away team form (5 games)
        away_form_5 = {}
        for col in ["wins", "draws", "losses", "points", "goals_scored", "goals_conceded", "clean_sheets"]:
            key = f"away_form_{col}_5"
            if key in row.index and pd.notna(row[key]):
                away_form_5[col] = float(row[key])
        if away_form_5:
            features["away_form_5"] = away_form_5

        # Away team form (10 games)
        away_form_10 = {}
        for col in ["wins", "draws", "losses", "points", "goals_scored", "goals_conceded", "clean_sheets"]:
            key = f"away_form_{col}_10"
            if key in row.index and pd.notna(row[key]):
                away_form_10[col] = float(row[key])
        if away_form_10:
            features["away_form_10"] = away_form_10

        # Rolling stats
        home_stats = {}
        away_stats = {}
        for stat in ["possession", "shots", "shots_on_target", "corners", "fouls"]:
            home_key = f"home_{stat}_avg_5"
            away_key = f"away_{stat}_avg_5"

            if home_key in row.index and pd.notna(row[home_key]):
                home_stats[stat] = float(row[home_key])
            if away_key in row.index and pd.notna(row[away_key]):
                away_stats[stat] = float(row[away_key])

        if home_stats:
            features["home_rolling_stats"] = home_stats
        if away_stats:
            features["away_rolling_stats"] = away_stats

        # Match outcomes (ground truth)
        outcomes = {}
        for col in ["result", "total_goals", "over_1_5", "over_2_5", "over_3_5", "btts", "home_clean_sheet", "away_clean_sheet"]:
            if col in row.index and pd.notna(row[col]):
                outcomes[col] = row[col]
        if outcomes:
            features["outcomes"] = outcomes

        # Match stats
        match_stats = {}
        for col in ["home_possessionPct", "home_totalShots", "home_shotsOnTarget", "home_wonCorners",
                    "away_possessionPct", "away_totalShots", "away_shotsOnTarget", "away_wonCorners"]:
            if col in row.index and pd.notna(row[col]):
                match_stats[col] = float(row[col])
        if match_stats:
            features["match_stats"] = match_stats

        return features

    async def get_import_stats(self) -> dict:
        """Get statistics about imported data."""
        async with self.async_session() as session:
            # Count fixtures with features
            result = await session.execute(
                text("SELECT COUNT(*) FROM fixtures WHERE features_metadata IS NOT NULL")
            )
            fixtures_with_features = result.scalar()

            # Total fixtures
            result = await session.execute(
                text("SELECT COUNT(*) FROM fixtures")
            )
            total_fixtures = result.scalar()

            return {
                "total_fixtures": total_fixtures,
                "fixtures_with_features": fixtures_with_features,
                "coverage_pct": round(fixtures_with_features / total_fixtures * 100, 2) if total_fixtures > 0 else 0,
            }

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()


async def main():
    """Main import function."""
    parser = argparse.ArgumentParser(description="Import processed match data")
    parser.add_argument("--dry-run", action="store_true", help="Don't commit changes")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size (rows per batch)")
    parser.add_argument("--max-workers", type=int, default=5, help="Maximum concurrent workers")
    args = parser.parse_args()

    print("🚀 FilterBets Data Import (Optimized)")
    print("=" * 50)

    # Create importer
    importer = DataImporter(settings.database_url, max_workers=args.max_workers)

    try:
        # Run import
        import time
        start_time = time.time()

        stats = await importer.import_from_csv(
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )

        elapsed_time = time.time() - start_time

        # Print results
        print("\n" + "=" * 50)
        print("📊 IMPORT SUMMARY")
        print("=" * 50)
        print(f"Total rows processed: {stats['total_rows']:,}")
        print(f"✅ Created: {stats['created']:,}")
        print(f"🔄 Updated: {stats['updated']:,}")
        print(f"⏭️  Skipped: {stats['skipped']:,}")
        print(f"❌ Errors: {stats['errors']:,}")
        print(f"⏱️  Time elapsed: {elapsed_time:.2f}s")
        print(f"⚡ Throughput: {stats['total_rows']/elapsed_time:.0f} rows/sec")

        if args.dry_run:
            print("\n⚠️  DRY RUN - No changes committed")
        else:
            print("\n✅ Import complete!")

            # Get final stats
            db_stats = await importer.get_import_stats()
            print("\n📈 Database Stats:")
            print(f"   Total fixtures: {db_stats['total_fixtures']:,}")
            print(f"   With features: {db_stats['fixtures_with_features']:,}")
            print(f"   Coverage: {db_stats['coverage_pct']}%")

    finally:
        await importer.close()


if __name__ == "__main__":
    asyncio.run(main())
