"""Fixture model mapped from ESPN fixtures.csv."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.filter_match import FilterMatch
    from app.models.league import League
    from app.models.team import Team
    from app.models.team_stats import TeamStats
    from app.models.venue import Venue


class Fixture(Base):
    """Football match/fixture model."""

    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    season_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    league_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("leagues.league_id"), nullable=False, index=True
    )
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    venue_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("venues.venue_id"), nullable=True
    )
    attendance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.team_id"), nullable=False, index=True
    )
    away_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.team_id"), nullable=False, index=True
    )
    home_team_winner: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    away_team_winner: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    home_team_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_team_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_team_shootout_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_team_shootout_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    features_metadata: Mapped[dict[str, Any] | None] = mapped_column("features_metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    league: Mapped[League] = relationship("League", back_populates="fixtures")
    venue: Mapped[Venue] = relationship("Venue", back_populates="fixtures")
    home_team: Mapped[Team] = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_fixtures"
    )
    away_team: Mapped[Team] = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_fixtures"
    )
    team_stats: Mapped[list[TeamStats]] = relationship(
        "TeamStats", back_populates="fixture"
    )
    filter_matches: Mapped[list[FilterMatch]] = relationship(
        "FilterMatch", back_populates="fixture", cascade="all, delete-orphan"
    )

    @property
    def is_finished(self) -> bool:
        """Check if match is finished (status_id 28 = Full Time)."""
        return self.status_id == 28

    @property
    def is_draw(self) -> bool:
        """Check if match ended in a draw."""
        if self.home_team_score is None or self.away_team_score is None:
            return False
        return self.home_team_score == self.away_team_score

    @property
    def total_goals(self) -> int:
        """Get total goals in the match."""
        home = self.home_team_score or 0
        away = self.away_team_score or 0
        return home + away

    @property
    def home_team_name(self) -> str | None:
        """Get home team name."""
        return self.home_team.name if self.home_team else None

    @property
    def away_team_name(self) -> str | None:
        """Get away team name."""
        return self.away_team.name if self.away_team else None

    @property
    def league_name(self) -> str | None:
        """Get league name."""
        return self.league.league_name if self.league else None

    @property
    def league_logo(self) -> str | None:
        """Get league logo."""
        return self.league.logo_url if self.league else None

    @property
    def home_team_logo(self) -> str | None:
        """Get home team logo."""
        return self.home_team.logo_url if self.home_team else None

    @property
    def away_team_logo(self) -> str | None:
        """Get away team logo."""
        return self.away_team.logo_url if self.away_team else None

    @property
    def home_score(self) -> int | None:
        """Get home team score (alias)."""
        return self.home_team_score

    @property
    def away_score(self) -> int | None:
        """Get away team score (alias)."""
        return self.away_team_score

    @property
    def home_odds(self) -> float | None:
        """Get home odds (placeholder)."""
        return None

    @property
    def draw_odds(self) -> float | None:
        """Get draw odds (placeholder)."""
        return None

    @property
    def away_odds(self) -> float | None:
        """Get away odds (placeholder)."""
        return None

    def __repr__(self) -> str:
        return f"<Fixture(id={self.id}, event_id={self.event_id})>"
