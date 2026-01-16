"""League model mapped from ESPN leagues.csv."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.standing import Standing


class League(Base):
    """Football league/competition model."""

    __tablename__ = "leagues"
    __table_args__ = (
        # Composite unique constraint for league_id + season_type + year
        # Same league can have multiple seasons
        UniqueConstraint("league_id", "season_type", "year", name="uq_league_season"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    season_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    season_name: Mapped[str] = mapped_column(String(255), nullable=False)
    season_slug: Mapped[str] = mapped_column(String(100), nullable=True)
    league_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    midsize_name: Mapped[str] = mapped_column(String(100), nullable=True)
    league_name: Mapped[str] = mapped_column(String(255), nullable=False)
    league_short_name: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    fixtures: Mapped[list[Fixture]] = relationship(
        "Fixture", back_populates="league"
    )
    standings: Mapped[list[Standing]] = relationship(
        "Standing", back_populates="league"
    )

    def __repr__(self) -> str:
        return f"<League(id={self.id}, name={self.league_name}, year={self.year})>"
