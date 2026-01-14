"""Scanner API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.scanner import ScannerStatusResponse, ScanTriggerResponse
from app.tasks.scanner_tasks import run_pre_match_scanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scanner", tags=["scanner"])


@router.get("/status", response_model=ScannerStatusResponse, operation_id="get_scanner_status")
async def get_scanner_status(
    current_user: User = Depends(get_current_user),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: ARG001
) -> ScannerStatusResponse:
    """Get scanner status and last run statistics.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        ScannerStatusResponse with scanner status
    """
    # TODO: Implement scanner status tracking in Redis or database
    # For now, return placeholder data
    return ScannerStatusResponse(
        last_scan_time=None,
        users_scanned=0,
        filters_evaluated=0,
        fixtures_checked=0,
        new_matches_found=0,
        notifications_queued=0,
        errors=0,
        scan_duration_seconds=0.0,
        next_scheduled_scan=None,
    )


@router.post("/trigger", response_model=ScanTriggerResponse, operation_id="trigger_scanner")
async def trigger_scanner(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),  # noqa: ARG001
) -> ScanTriggerResponse:
    """Manually trigger a scanner run (admin only).

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        ScanTriggerResponse with task ID

    Raises:
        HTTPException: If user is not an admin
    """
    # Check if user is admin
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can manually trigger scanner",
        )

    # Trigger scanner task
    task = run_pre_match_scanner.delay()

    logger.info(f"Scanner manually triggered by user {current_user.id}, task: {task.id}")

    return ScanTriggerResponse(
        task_id=task.id,
        message="Scanner task queued successfully",
        estimated_completion_seconds=60,
    )
