"""BacktestJob model for async backtest job tracking."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.filter import Filter
    from app.models.user import User


class BacktestJob(Base):
    """Async backtest job tracking model."""

    __tablename__ = "backtest_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )  # pending, running, completed, failed, cancelled
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Request parameters
    bet_type: Mapped[str] = mapped_column(String(20), nullable=False)
    seasons: Mapped[str] = mapped_column(String(100), nullable=False)  # Comma-separated

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="backtest_jobs")
    filter: Mapped[Filter] = relationship("Filter", back_populates="backtest_jobs")

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

    def __repr__(self) -> str:
        return f"<BacktestJob(id={self.id}, job_id={self.job_id}, status={self.status})>"
