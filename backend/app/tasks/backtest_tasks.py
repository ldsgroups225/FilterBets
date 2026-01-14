"""Celery tasks for async backtest execution."""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.backtest_job import BacktestJob
from app.models.filter import Filter
from app.schemas.backtest import BacktestRequest, BetType
from app.services.backtest import BacktestService
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
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session_maker()


@celery_app.task(name="app.tasks.backtest_tasks.run_async_backtest", bind=True)
def run_async_backtest(
    self: Any,
    job_id: str,
    filter_id: int,
    bet_type: str,
    seasons: list[int],
    stake: float = 1.0,
) -> dict[str, Any]:
    """
    Celery task to run backtest asynchronously.

    Args:
        job_id: BacktestJob UUID
        filter_id: Filter ID
        bet_type: Type of bet
        seasons: List of season years
        stake: Stake amount per bet

    Returns:
        Dictionary with task results
    """
    import asyncio

    async def _run_backtest() -> dict[str, Any]:
        session = get_async_session()
        try:
            # Get the job
            job_uuid = UUID(job_id)
            result = await session.execute(
                select(BacktestJob).where(BacktestJob.job_id == job_uuid)
            )
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"BacktestJob {job_id} not found")

            # Update job status to running
            job.status = "running"
            job.started_at = datetime.utcnow()
            job.progress = 10
            await session.commit()

            # Get the filter
            filter_result = await session.execute(
                select(Filter).where(Filter.id == filter_id)
            )
            filter_obj = filter_result.scalar_one_or_none()

            if not filter_obj:
                job.status = "failed"
                job.error_message = f"Filter {filter_id} not found"
                job.completed_at = datetime.utcnow()
                await session.commit()
                raise ValueError(f"Filter {filter_id} not found")

            # Update progress
            job.progress = 30
            await session.commit()

            # Run the backtest
            backtest_service = BacktestService(session)
            request = BacktestRequest(
                bet_type=BetType(bet_type),
                seasons=seasons,
                stake=stake,
            )

            # Update progress
            job.progress = 50
            await session.commit()

            # Execute backtest with analytics
            response = await backtest_service.run_backtest(
                filter_obj, request, include_analytics=True
            )

            # Update progress
            job.progress = 90
            await session.commit()

            # Store result
            job.status = "completed"
            job.progress = 100
            job.result = response.model_dump(mode="json")
            job.completed_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Successfully completed backtest job {job_id}")

            return {
                "status": "success",
                "job_id": job_id,
                "filter_id": filter_id,
                "total_matches": response.total_matches,
                "win_rate": response.win_rate,
                "roi_percentage": response.roi_percentage,
            }

        except Exception as e:
            logger.error(f"Error running backtest job {job_id}: {e}")

            # Update job status to failed
            try:
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.completed_at = datetime.utcnow()
                    await session.commit()
            except Exception as commit_error:
                logger.error(f"Error updating job status: {commit_error}")

            raise
        finally:
            await session.close()

    return asyncio.run(_run_backtest())
