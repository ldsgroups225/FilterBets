"""Standing model mapped from ESPN standings.csv."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.league import League
    from app.models.team import Team


class Standing(Base):
    """League standings/table model."""

    __tablename__ = "standings"

    __table_args__ = (
        UniqueConstraint(
            "season_type", "league_id", "team_id", name="uq_standing_season_league_team"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    season_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    league_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("leagues.league_id"), nullable=False, index=True
    )
    last_match_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    team_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.team_id"), nullable=False, index=True
    )
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    ties: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    goals_for: Mapped[float | None] = mapped_column(Float, nullable=True)
    goals_against: Mapped[float | None] = mapped_column(Float, nullable=True)
    goal_difference: Mapped[float | None] = mapped_column(Float, nullable=True)
    deductions: Mapped[int] = mapped_column(Integer, default=0)
    clean_sheets: Mapped[float | None] = mapped_column(Float, nullable=True)
    form: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g., "WDWWW"
    next_opponent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_home_away: Mapped[str | None] = mapped_column(String(10), nullable=True)
    next_match_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    league: Mapped[League] = relationship("League", back_populates="standings")
    team: Mapped[Team] = relationship("Team", back_populates="standings")

    def __repr__(self) -> str:
        return f"<Standing(id={self.id}, team_id={self.team_id}, rank={self.team_rank})>"
