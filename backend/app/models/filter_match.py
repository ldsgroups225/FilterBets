"""FilterMatch model for tracking matches that triggered filters."""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BetResult(str, PyEnum):
    """Bet outcome status."""

    PENDING = "pending"
    WIN = "win"
    LOSS = "loss"
    PUSH = "push"  # Draw/void


class FilterMatch(Base):
    """Tracks matches that triggered a user's filter and notification status."""

    __tablename__ = "filter_matches"
    __table_args__ = (
        UniqueConstraint("filter_id", "fixture_id", name="uq_filter_fixture"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fixture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notification_sent: Mapped[bool] = mapped_column(default=False)
    notification_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notification_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bet_result: Mapped[BetResult] = mapped_column(
        Enum(BetResult, native_enum=False, length=20),
        default=BetResult.PENDING,
        nullable=False,
    )

    # Relationships
    filter: Mapped["Filter"] = relationship("Filter", back_populates="filter_matches")  # noqa: F821
    fixture: Mapped["Fixture"] = relationship("Fixture", back_populates="filter_matches")  # noqa: F821

    def __repr__(self) -> str:
        return f"<FilterMatch(id={self.id}, filter_id={self.filter_id}, fixture_id={self.fixture_id})>"
