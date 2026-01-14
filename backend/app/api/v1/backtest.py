"""Backtest job management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.backtest_job import BacktestJob
from app.models.user import User
from app.schemas.backtest_job import BacktestJobList, BacktestJobResponse, BacktestJobStatus

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/jobs", response_model=BacktestJobList)
async def list_backtest_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: Annotated[str | None, Query()] = None,
) -> BacktestJobList:
    """
    List backtest jobs for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        status: Optional status filter

    Returns:
        List of backtest jobs with pagination
    """
    # Build query
    query = select(BacktestJob).where(BacktestJob.user_id == current_user.id)

    if status:
        query = query.where(BacktestJob.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = (
        query.order_by(BacktestJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    # Execute query
    result = await db.execute(query)
    jobs = list(result.scalars().all())

    return BacktestJobList(
        jobs=[BacktestJobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/jobs/{job_id}", response_model=BacktestJobStatus)
async def get_backtest_job_status(
    job_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BacktestJobStatus:
    """
    Get status of a specific backtest job.

    Args:
        job_id: Job UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Job status information

    Raises:
        HTTPException: 404 if job not found or not owned by user
    """
    # Get job
    result = await db.execute(
        select(BacktestJob).where(
            and_(
                BacktestJob.job_id == job_id,
                BacktestJob.user_id == current_user.id,
            )
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Backtest job not found",
        )

    return BacktestJobStatus(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result=job.result,
        error_message=job.error_message,
    )


@router.delete("/jobs/{job_id}")
async def cancel_backtest_job(
    job_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Cancel a pending or running backtest job.

    Args:
        job_id: Job UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: 404 if job not found, 400 if job cannot be cancelled
    """
    # Get job
    result = await db.execute(
        select(BacktestJob).where(
            and_(
                BacktestJob.job_id == job_id,
                BacktestJob.user_id == current_user.id,
            )
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Backtest job not found",
        )

    # Check if job can be cancelled
    if job.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}",
        )

    # Update job status
    job.status = "cancelled"
    await db.commit()

    return {"message": "Backtest job cancelled successfully"}
