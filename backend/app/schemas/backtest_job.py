"""Backtest job schemas for async job management."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class BacktestJobCreate(BaseModel):
    """Schema for creating a backtest job."""

    bet_type: str = Field(..., description="Type of bet to evaluate")
    seasons: list[int] = Field(..., min_length=1, max_length=5, description="Season years")
    stake: float = Field(default=1.0, gt=0, description="Flat stake amount per bet")
    async_mode: bool = Field(
        default=True, description="Whether to run asynchronously (default: True)"
    )


class BacktestJobResponse(BaseModel):
    """Schema for backtest job response."""

    id: int
    job_id: UUID
    user_id: int
    filter_id: int
    status: str  # pending, running, completed, failed, cancelled
    progress: int  # 0-100
    result: dict[str, Any] | None
    error_message: str | None
    bet_type: str
    seasons: str  # Comma-separated
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class BacktestJobStatus(BaseModel):
    """Schema for backtest job status check."""

    job_id: UUID
    status: str
    progress: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: dict[str, Any] | None = None
    error_message: str | None = None

    @property
    def is_pending(self) -> bool:
        """Check if job is pending."""
        return self.status == "pending"

    @property
    def is_running(self) -> bool:
        """Check if job is running."""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == "failed"


class BacktestJobList(BaseModel):
    """Schema for listing backtest jobs."""

    jobs: list[BacktestJobResponse]
    total: int
    page: int
    page_size: int
