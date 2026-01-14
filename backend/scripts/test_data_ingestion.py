#!/usr/bin/env python3
"""Script to test data ingestion and verify row counts."""

import asyncio
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Fixture, League, Standing, Team, TeamStats, Venue
from app.services.data_ingestion import DataIngestionService


async def test_ingestion():
    """Test data ingestion and print row counts."""
    settings = get_settings()

    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Initialize ingestion service
        data_dir = Path(__file__).parent.parent.parent / "data" / "base_data"
        service = DataIngestionService(session, data_dir)

        print("Starting data ingestion...")
        print(f"Data directory: {data_dir}")
        print("-" * 60)

        # Run ingestion
        results = await service.ingest_all()

        print("\nIngestion Results:")
        print("-" * 60)
        for entity, count in results.items():
            print(f"{entity.capitalize()}: {count} records inserted")

        # Verify counts in database
        print("\nDatabase Row Counts:")
        print("-" * 60)

        venue_count = await session.scalar(select(func.count()).select_from(Venue))
        print(f"Venues: {venue_count}")

        league_count = await session.scalar(select(func.count()).select_from(League))
        print(f"Leagues: {league_count}")

        team_count = await session.scalar(select(func.count()).select_from(Team))
        print(f"Teams: {team_count}")

        fixture_count = await session.scalar(select(func.count()).select_from(Fixture))
        print(f"Fixtures: {fixture_count}")

        stats_count = await session.scalar(select(func.count()).select_from(TeamStats))
        print(f"Team Stats: {stats_count}")

        standing_count = await session.scalar(select(func.count()).select_from(Standing))
        print(f"Standings: {standing_count}")

        print("-" * 60)
        print("\nSample Data:")
        print("-" * 60)

        # Show sample league
        league = await session.scalar(select(League).limit(1))
        if league:
            print(f"\nSample League: {league.league_name} ({league.year})")

        # Show sample team
        team = await session.scalar(select(Team).limit(1))
        if team:
            print(f"Sample Team: {team.display_name}")

        # Show sample fixture
        fixture = await session.scalar(select(Fixture).limit(1))
        if fixture:
            print(f"Sample Fixture: Event ID {fixture.event_id} on {fixture.match_date}")

        print("\n✓ Data ingestion test completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_ingestion())
