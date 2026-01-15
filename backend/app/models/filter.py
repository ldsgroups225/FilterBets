"""Filter model for user-defined betting strategies."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.backtest_job import BacktestJob
    from app.models.backtest_result import BacktestResult
    from app.models.filter_match import FilterMatch
    from app.models.user import User


class Filter(Base):
    """User-defined filter strategy model."""

    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="filters")
    backtest_results: Mapped[list[BacktestResult]] = relationship(
        "BacktestResult", back_populates="filter", cascade="all, delete-orphan"
    )
    backtest_jobs: Mapped[list[BacktestJob]] = relationship(
        "BacktestJob", back_populates="filter", cascade="all, delete-orphan"
    )
    filter_matches: Mapped[list[FilterMatch]] = relationship(
        "FilterMatch", back_populates="filter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Filter(id={self.id}, name={self.name}, user_id={self.user_id})>"
