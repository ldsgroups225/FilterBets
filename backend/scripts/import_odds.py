#!/usr/bin/env python3
"""
Import historical odds data into the FilterBets database.

This script loads betting odds from CSV/Parquet files and stores them
in the fixtures' features_metadata JSON field for use in backtesting.

Usage:
    poetry run python backend/scripts/import_odds.py --help
    poetry run python backend/scripts/import_odds.py --file data/odds.csv
    poetry run python backend/scripts/import_odds.py --file data/odds.parquet --dry-run
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.fixture import Fixture

settings = get_settings()


class OddsImporter:
    """Import historical betting odds into the database."""

    def __init__(self, db_url: str, max_workers: int = 5):
        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=max_workers + 2,
            max_overflow=max_workers * 2,
            pool_pre_ping=True,
        )
        self.async_session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )  # type: ignore
        self.stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0}

    async def import_from_csv(
        self, file_path: str, dry_run: bool = False, bookmaker: str = "default"
    ) -> dict:
        """Import odds from a CSV file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"📂 Loading odds from {path}")
        df = pd.read_csv(path)
        print(f"✅ Loaded {len(df):,} odds records")

        required_columns = {"event_id", "home_odds", "draw_odds", "away_odds"}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.stats["total"] = len(df)
        await self._process_odds_batch(df, bookmaker, dry_run)

        return self.stats

    async def import_from_parquet(
        self, file_path: str, dry_run: bool = False, bookmaker: str = "default"
    ) -> dict:
        """Import odds from a Parquet file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"📂 Loading odds from {path}")
        df = pd.read_parquet(path)
        print(f"✅ Loaded {len(df):,} odds records")

        required_columns = {"event_id", "home_odds", "draw_odds", "away_odds"}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.stats["total"] = len(df)
        await self._process_odds_batch(df, bookmaker, dry_run)

        return self.stats

    async def _process_odds_batch(
        self, df: pd.DataFrame, bookmaker: str, dry_run: bool
    ):
        """Process odds data in batches and update fixtures."""
        batch_size = 500
        total = len(df)

        for i in range(0, total, batch_size):
            batch = df.iloc[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size

            async with self.async_session() as session:
                event_ids = batch["event_id"].dropna().astype(int).tolist()

                fixtures_result = await session.execute(
                    select(Fixture).where(Fixture.event_id.in_(event_ids))
                )
                fixtures = {f.event_id: f for f in fixtures_result.scalars().all()}

                for _, row in batch.iterrows():
                    event_id = row.get("event_id")
                    if event_id is None or pd.isna(event_id):
                        self.stats["skipped"] += 1
                        continue

                    event_id = int(event_id)
                    if event_id not in fixtures:
                        self.stats["skipped"] += 1
                        continue

                    fixture = fixtures[event_id]
                    home_odds = row.get("home_odds")
                    draw_odds = row.get("draw_odds")
                    away_odds = row.get("away_odds")

                    if pd.isna(home_odds) or pd.isna(draw_odds) or pd.isna(away_odds):
                        self.stats["skipped"] += 1
                        continue

                    odds_data = {
                        "bookmaker": bookmaker,
                        "home_odds": float(home_odds),
                        "draw_odds": float(draw_odds),
                        "away_odds": float(away_odds),
                    }

                    if fixture.features_metadata is None:
                        fixture.features_metadata = {}
                    fixture.features_metadata["odds"] = odds_data
                    self.stats["updated"] += 1

            if not dry_run:
                await session.commit()
            else:
                await session.rollback()

            progress = min(i + batch_size, total)
            print(f"⏳ Batch {batch_num}/{total_batches}: {progress:,}/{total:,} ({progress/total*100:.1f}%) | U:{self.stats['updated']} S:{self.stats['skipped']}")

    async def get_odds_stats(self) -> dict:
        """Get statistics about imported odds."""
        async with self.async_session() as session:
            result = await session.execute(
                select(Fixture).where(
                    Fixture.features_metadata["odds"].astext.isnot(None)
                )
            )
            fixtures_with_odds = len(result.scalars().all())

            result = await session.execute(select(Fixture))
            total_fixtures = len(result.scalars().all())

            return {
                "total_fixtures": total_fixtures,
                "with_odds": fixtures_with_odds,
                "coverage_pct": round(fixtures_with_odds / total_fixtures * 100, 2) if total_fixtures > 0 else 0,
            }

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()


async def main():
    parser = argparse.ArgumentParser(description="Import historical betting odds")
    parser.add_argument("--file", "-f", required=True, help="Path to CSV or Parquet file")
    parser.add_argument(
        "--bookmaker", "-b", default="default", help="Bookmaker name (default: default)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't commit changes"
    )
    parser.add_argument(
        "--max-workers", type=int, default=5, help="Maximum concurrent workers"
    )
    args = parser.parse_args()

    print("🚀 FilterBets Odds Import")
    print("=" * 50)

    importer = OddsImporter(settings.database_url, max_workers=args.max_workers)

    try:
        file_path = Path(args.file)
        if file_path.suffix == ".csv":
            stats = await importer.import_from_csv(
                args.file, dry_run=args.dry_run, bookmaker=args.bookmaker
            )
        elif file_path.suffix in [".parquet", ".pq"]:
            stats = await importer.import_from_parquet(
                args.file, dry_run=args.dry_run, bookmaker=args.bookmaker
            )
        else:
            raise ValueError("Unsupported file format. Use CSV or Parquet.")

        print("\n" + "=" * 50)
        print("📊 IMPORT SUMMARY")
        print("=" * 50)
        print(f"Total records: {stats['total']:,}")
        print(f"✅ Updated: {stats['updated']:,}")
        print(f"⏭️  Skipped: {stats['skipped']:,}")
        print(f"❌ Errors: {stats['errors']:,}")

        if args.dry_run:
            print("\n⚠️  DRY RUN - No changes committed")
        else:
            print("\n✅ Import complete!")
            odds_stats = await importer.get_odds_stats()
            print("\n📈 Database Stats:")
            print(f"   Total fixtures: {odds_stats['total_fixtures']:,}")
            print(f"   With odds: {odds_stats['with_odds']:,}")
            print(f"   Coverage: {odds_stats['coverage_pct']}%")

    finally:
        await importer.close()


if __name__ == "__main__":
    asyncio.run(main())
