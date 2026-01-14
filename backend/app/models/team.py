"""Team model mapped from ESPN teams.csv."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Team(Base):
    """Football team model."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(10), nullable=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    color: Mapped[str] = mapped_column(String(10), nullable=True)
    alternate_color: Mapped[str] = mapped_column(String(10), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    venue_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("venues.venue_id"), nullable=True
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    venue: Mapped["Venue"] = relationship("Venue", back_populates="teams")  # noqa: F821
    home_fixtures: Mapped[list["Fixture"]] = relationship(  # noqa: F821
        "Fixture",
        foreign_keys="Fixture.home_team_id",
        back_populates="home_team",
    )
    away_fixtures: Mapped[list["Fixture"]] = relationship(  # noqa: F821
        "Fixture",
        foreign_keys="Fixture.away_team_id",
        back_populates="away_team",
    )
    stats: Mapped[list["TeamStats"]] = relationship(  # noqa: F821
        "TeamStats", back_populates="team"
    )
    standings: Mapped[list["Standing"]] = relationship(  # noqa: F821
        "Standing", back_populates="team"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name={self.display_name})>"
