"""Pydantic schemas for scanner endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class ScannerStatusResponse(BaseModel):
    """Scanner status information."""

    last_scan_time: datetime | None = Field(None, description="Last scan timestamp")
    users_scanned: int = Field(0, description="Users scanned in last run")
    filters_evaluated: int = Field(0, description="Filters evaluated in last run")
    fixtures_checked: int = Field(0, description="Fixtures checked in last run")
    new_matches_found: int = Field(0, description="New matches found in last run")
    notifications_queued: int = Field(0, description="Notifications queued in last run")
    errors: int = Field(0, description="Errors in last run")
    scan_duration_seconds: float = Field(0.0, description="Last scan duration")
    next_scheduled_scan: datetime | None = Field(
        None, description="Next scheduled scan time"
    )

    model_config = {"from_attributes": True}


class ScanTriggerResponse(BaseModel):
    """Response for manually triggering a scan."""

    task_id: str = Field(..., description="Celery task ID")
    message: str = Field(..., description="Status message")
    estimated_completion_seconds: int = Field(
        ..., description="Estimated time to complete"
    )

    model_config = {"from_attributes": True}
