"""Celery tasks for team statistics calculation."""

import logging
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.services.team_stats_calculator import TeamStatsCalculator
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def get_async_session() -> AsyncSession:
    """Create async database session for Celery tasks."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return session_factory()


@celery_app.task(name="app.tasks.stats_tasks.refresh_all_team_stats_task", bind=True)  # type: ignore[untyped-decorator]
def refresh_all_team_stats_task(_self: Any, season_type: int | None = None) -> dict[str, Any]:
    """
    Celery task to refresh computed stats for all teams.

    Args:
        season_type: Optional season year to refresh (defaults to all seasons)

    Returns:
        Dictionary with task results
    """
    import asyncio

    async def _refresh_stats() -> dict[str, Any]:
        session = get_async_session()
        try:
            calculator = TeamStatsCalculator(session)
            count = await calculator.refresh_all_team_stats(season_type)

            logger.info(f"Successfully refreshed stats for {count} team-season combinations")

            return {
                "status": "success",
                "teams_refreshed": count,
                "season_type": season_type,
            }
        except Exception as e:
            logger.error(f"Error refreshing team stats: {e}")
            raise
        finally:
            await session.close()

    # Run the async function
    return asyncio.run(_refresh_stats())


@celery_app.task(name="app.tasks.stats_tasks.refresh_team_stats_task", bind=True)  # type: ignore[untyped-decorator]
def refresh_team_stats_task(
    _self: Any, team_id: int, season_type: int
) -> dict[str, Any]:
    """
    Celery task to refresh computed stats for a specific team and season.

    Args:
        team_id: Team ID
        season_type: Season year

    Returns:
        Dictionary with task results
    """
    import asyncio

    async def _refresh_stats() -> dict[str, Any]:
        session = get_async_session()
        try:
            calculator = TeamStatsCalculator(session)
            stats = await calculator.refresh_team_stats(team_id, season_type)

            logger.info(f"Successfully refreshed stats for team {team_id}, season {season_type}")

            return {
                "status": "success",
                "team_id": team_id,
                "season_type": season_type,
                "stats_id": stats.id,
            }
        except Exception as e:
            logger.error(f"Error refreshing team stats: {e}")
            raise
        finally:
            await session.close()

    return asyncio.run(_refresh_stats())
