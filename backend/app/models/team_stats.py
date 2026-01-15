"""TeamStats model mapped from ESPN teamStats.csv."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.team import Team


class TeamStats(Base):
    """Per-match team statistics model."""

    __tablename__ = "team_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    season_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixtures.event_id"), nullable=False, index=True
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.team_id"), nullable=False, index=True
    )
    team_order: Mapped[int] = mapped_column(Integer, nullable=True)  # 0=home, 1=away
    possession_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    fouls_committed: Mapped[float | None] = mapped_column(Float, nullable=True)
    yellow_cards: Mapped[float | None] = mapped_column(Float, nullable=True)
    red_cards: Mapped[float | None] = mapped_column(Float, nullable=True)
    offsides: Mapped[float | None] = mapped_column(Float, nullable=True)
    won_corners: Mapped[float | None] = mapped_column(Float, nullable=True)
    saves: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_shots: Mapped[float | None] = mapped_column(Float, nullable=True)
    shots_on_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    shot_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    penalty_kick_goals: Mapped[float | None] = mapped_column(Float, nullable=True)
    penalty_kick_shots: Mapped[float | None] = mapped_column(Float, nullable=True)
    accurate_passes: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_passes: Mapped[float | None] = mapped_column(Float, nullable=True)
    pass_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    accurate_crosses: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_crosses: Mapped[float | None] = mapped_column(Float, nullable=True)
    cross_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_long_balls: Mapped[float | None] = mapped_column(Float, nullable=True)
    accurate_long_balls: Mapped[float | None] = mapped_column(Float, nullable=True)
    longball_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    blocked_shots: Mapped[float | None] = mapped_column(Float, nullable=True)
    effective_tackles: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_tackles: Mapped[float | None] = mapped_column(Float, nullable=True)
    tackle_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    interceptions: Mapped[float | None] = mapped_column(Float, nullable=True)
    effective_clearance: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_clearance: Mapped[float | None] = mapped_column(Float, nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    fixture: Mapped[Fixture] = relationship(
        "Fixture", back_populates="team_stats"
    )
    team: Mapped[Team] = relationship("Team", back_populates="stats")

    def __repr__(self) -> str:
        return f"<TeamStats(id={self.id}, event_id={self.event_id}, team_id={self.team_id})>"
