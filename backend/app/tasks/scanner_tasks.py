"""Celery tasks for pre-match scanning."""

import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.filter_match import FilterMatch
from app.services.scanner_service import PreMatchScanner
from app.tasks.celery_app import celery_app
from app.tasks.notification_tasks import send_filter_alert

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async database session factory for tasks
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


@celery_app.task(name="app.tasks.scanner_tasks.run_pre_match_scanner", bind=True)
def run_pre_match_scanner(_self: Any) -> dict[str, Any]:
    """Run the pre-match scanner and queue notifications.

    Args:
        _self: Celery task instance (unused but required by bind=True)

    Returns:
        Dictionary with scan statistics
    """
    return asyncio.run(_run_pre_match_scanner_async())


async def _run_pre_match_scanner_async() -> dict[str, Any]:
    """Async implementation of pre-match scanner.

    Returns:
        Dictionary with scan statistics
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting pre-match scanner task")

            # Run scanner
            scanner = PreMatchScanner(db)
            stats = await scanner.run_full_scan()

            # Queue notifications for new matches
            if stats.new_matches_found > 0:
                # Get filter matches that need notifications
                result = await db.execute(
                    select(FilterMatch)
                    .where(FilterMatch.notification_sent == False)  # noqa: E712
                    .order_by(FilterMatch.matched_at)
                    .limit(settings.scanner_max_notifications_per_scan)
                )
                filter_matches = list(result.scalars().all())

                # Queue notification tasks
                for filter_match in filter_matches:
                    send_filter_alert.delay(filter_match.id)
                    logger.info(f"Queued notification for FilterMatch {filter_match.id}")

            # Return stats
            return {
                "status": "success",
                "users_scanned": stats.users_scanned,
                "filters_evaluated": stats.filters_evaluated,
                "fixtures_checked": stats.fixtures_checked,
                "new_matches_found": stats.new_matches_found,
                "notifications_queued": stats.notifications_queued,
                "errors": stats.errors,
                "scan_duration_seconds": stats.scan_duration_seconds,
            }

        except Exception as e:
            logger.error(f"Error in pre-match scanner task: {e}")
            return {
                "status": "error",
                "message": str(e),
            }
