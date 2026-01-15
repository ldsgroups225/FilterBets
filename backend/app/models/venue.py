"""Venue model mapped from ESPN venues.csv."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.team import Team


class Venue(Base):
    """Stadium/venue model."""

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    short_name: Mapped[str] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    teams: Mapped[list[Team]] = relationship("Team", back_populates="venue")
    fixtures: Mapped[list[Fixture]] = relationship(
        "Fixture", back_populates="venue"
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name={self.full_name})>"
