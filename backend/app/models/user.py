"""User model for authentication."""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.backtest_job import BacktestJob
    from app.models.filter import Filter


class ScanFrequency(str, PyEnum):
    """Scan frequency options for users."""

    TWICE_DAILY = "2x"  # Free tier: 8 AM and 2 PM UTC
    FOUR_TIMES_DAILY = "4x"  # Premium: 6 AM, 11 AM, 4 PM, 9 PM UTC
    SIX_TIMES_DAILY = "6x"  # Premium: every 4 hours starting at 2 AM UTC


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    scan_frequency: Mapped[ScanFrequency] = mapped_column(
        Enum(ScanFrequency, values_callable=lambda x: [e.value for e in x], native_enum=False, length=5),
        default=ScanFrequency.TWICE_DAILY,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    filters: Mapped[list[Filter]] = relationship(
        "Filter", back_populates="user", cascade="all, delete-orphan"
    )
    backtest_jobs: Mapped[list[BacktestJob]] = relationship(
        "BacktestJob", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
