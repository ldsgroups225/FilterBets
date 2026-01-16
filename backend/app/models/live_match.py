"""Live match model for real-time match tracking."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LiveMatch(Base):
    """Live match data for real-time filtering."""

    __tablename__ = "live_matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fixture_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Match status and timing
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # LIVE, HALFTIME, FULLTIME, etc.
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Score
    home_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Live stats - JSON structure for flexibility
    live_stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Team states
    home_team_state: Mapped[str | None] = mapped_column(String(20))  # WINNING, LOSING, DRAWING, etc.
    away_team_state: Mapped[str | None] = mapped_column(String(20))
    momentum: Mapped[str | None] = mapped_column(String(10))  # HOME, AWAY, NEUTRAL

    # AI predictions (mock data)
    ai_predictions: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Historical stats (mock data)
    historical_stats: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class LiveOdds(Base):
    """Live odds data for real-time filtering."""

    __tablename__ = "live_odds"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fixture_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Market information
    market_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 1X2, OU, BTTS, CORNERS
    selection: Mapped[str] = mapped_column(String(20), nullable=False)  # HOME, OVER, YES, etc.
    line: Mapped[float | None] = mapped_column(Float)  # For OU/Corners (e.g., 2.5)

    # Odds value
    odds: Mapped[float] = mapped_column(Float, nullable=False)

    # Timestamp
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LiveFilterResult(Base):
    """Results from live filter execution with dual-stat comparison."""

    __tablename__ = "live_filter_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filter_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fixture_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # When the filter was triggered
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    triggered_minute: Mapped[int] = mapped_column(Integer, nullable=False)

    # Stats at notification moment (bell icon)
    notification_value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Final/current stats (flag icon)
    final_value: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Result tracking
    bet_result: Mapped[str] = mapped_column(String(10), default="PENDING")  # PENDING, WIN, LOSS, PUSH
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Odds at trigger moment
    odds_at_trigger: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
