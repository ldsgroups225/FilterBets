#!/usr/bin/env python3
"""Script to check data counts in the database."""

import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Fixture, League, Standing, Team, TeamStats, Venue


async def check_counts():
    """Check row counts in database."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Database Row Counts:")
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
        print("\n✓ Data check completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_counts())
