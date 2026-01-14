"""BacktestResult model for cached backtest results."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BacktestResult(Base):
    """Cached backtest result model."""

    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filter_id: Mapped[int] = mapped_column(
        ForeignKey("filters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bet_type: Mapped[str] = mapped_column(String(20), nullable=False)
    seasons: Mapped[str] = mapped_column(String(100), nullable=False)  # Comma-separated
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    pushes: Mapped[int] = mapped_column(Integer, default=0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    total_profit: Mapped[float] = mapped_column(Float, default=0.0)
    roi_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    avg_odds: Mapped[float | None] = mapped_column(Float, nullable=True)
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    filter: Mapped["Filter"] = relationship(  # noqa: F821
        "Filter", back_populates="backtest_results"
    )

    @property
    def is_expired(self) -> bool:
        """Check if the cached result has expired."""
        return datetime.utcnow() > self.expires_at

    def __repr__(self) -> str:
        return f"<BacktestResult(id={self.id}, filter_id={self.filter_id}, win_rate={self.win_rate})>"
