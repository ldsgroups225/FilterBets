"""Filter model for user-defined betting strategies."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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
    user: Mapped["User"] = relationship("User", back_populates="filters")  # noqa: F821
    backtest_results: Mapped[list["BacktestResult"]] = relationship(  # noqa: F821
        "BacktestResult", back_populates="filter", cascade="all, delete-orphan"
    )
    backtest_jobs: Mapped[list["BacktestJob"]] = relationship(  # noqa: F821
        "BacktestJob", back_populates="filter", cascade="all, delete-orphan"
    )
    filter_matches: Mapped[list["FilterMatch"]] = relationship(  # noqa: F821
        "FilterMatch", back_populates="filter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Filter(id={self.id}, name={self.name}, user_id={self.user_id})>"
