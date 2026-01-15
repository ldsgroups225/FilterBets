"""TeamComputedStats model for pre-computed team statistics."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.team import Team


class TeamComputedStats(Base):
    """Pre-computed team statistics for efficient filtering."""

    __tablename__ = "team_computed_stats"
    __table_args__ = (
        UniqueConstraint("team_id", "season_type", name="uq_team_season_stats"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.team_id"), nullable=False, index=True
    )
    season_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Overall stats
    matches_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    goals_scored: Mapped[int] = mapped_column(Integer, default=0)
    goals_conceded: Mapped[int] = mapped_column(Integer, default=0)
    goals_scored_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)
    goals_conceded_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)
    clean_sheets: Mapped[int] = mapped_column(Integer, default=0)
    clean_sheet_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    failed_to_score: Mapped[int] = mapped_column(Integer, default=0)
    failed_to_score_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    points_per_game: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)

    # Home stats
    home_matches: Mapped[int] = mapped_column(Integer, default=0)
    home_wins: Mapped[int] = mapped_column(Integer, default=0)
    home_draws: Mapped[int] = mapped_column(Integer, default=0)
    home_losses: Mapped[int] = mapped_column(Integer, default=0)
    home_goals_scored_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)
    home_goals_conceded_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)

    # Away stats
    away_matches: Mapped[int] = mapped_column(Integer, default=0)
    away_wins: Mapped[int] = mapped_column(Integer, default=0)
    away_draws: Mapped[int] = mapped_column(Integer, default=0)
    away_losses: Mapped[int] = mapped_column(Integer, default=0)
    away_goals_scored_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)
    away_goals_conceded_avg: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=0)

    # Form (last 5 games)
    form_last5_wins: Mapped[int] = mapped_column(Integer, default=0)
    form_last5_draws: Mapped[int] = mapped_column(Integer, default=0)
    form_last5_losses: Mapped[int] = mapped_column(Integer, default=0)
    form_last5_points: Mapped[int] = mapped_column(Integer, default=0)
    form_last5_goals_scored: Mapped[int] = mapped_column(Integer, default=0)
    form_last5_goals_conceded: Mapped[int] = mapped_column(Integer, default=0)

    # Form (last 10 games)
    form_last10_wins: Mapped[int] = mapped_column(Integer, default=0)
    form_last10_draws: Mapped[int] = mapped_column(Integer, default=0)
    form_last10_losses: Mapped[int] = mapped_column(Integer, default=0)
    form_last10_points: Mapped[int] = mapped_column(Integer, default=0)

    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    team: Mapped[Team] = relationship("Team", back_populates="computed_stats")

    def __repr__(self) -> str:
        return f"<TeamComputedStats(team_id={self.team_id}, season={self.season_type})>"
