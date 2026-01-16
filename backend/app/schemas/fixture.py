"""Fixture schemas for API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class FixtureResponse(BaseModel):
    """Fixture response schema."""

    id: int = Field(..., description="Fixture database ID")
    event_id: int = Field(..., description="ESPN event ID")
    season_type: int = Field(..., description="Season type identifier")
    league_id: int = Field(..., description="League ID")
    match_date: datetime = Field(..., description="Match date and time")
    venue_id: int | None = Field(None, description="Venue ID")
    attendance: int | None = Field(None, description="Match attendance")
    home_team_id: int = Field(..., description="Home team ID")
    away_team_id: int = Field(..., description="Away team ID")
    home_team_winner: bool | None = Field(None, description="Whether home team won")
    away_team_winner: bool | None = Field(None, description="Whether away team won")
    home_team_score: int | None = Field(None, description="Home team score")
    away_team_score: int | None = Field(None, description="Away team score")
    home_team_shootout_score: int | None = Field(None, description="Home team shootout score")
    away_team_shootout_score: int | None = Field(None, description="Away team shootout score")
    status_id: int = Field(..., description="Match status ID")
    update_time: datetime | None = Field(None, description="Last update timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")

    # Flattened fields for frontend
    home_team_name: str | None = Field(None, description="Home team name")
    away_team_name: str | None = Field(None, description="Away team name")
    league_name: str | None = Field(None, description="League name")
    home_team_logo: str | None = Field(None, description="Home team logo URL")
    away_team_logo: str | None = Field(None, description="Away team logo URL")
    league_logo: str | None = Field(None, description="League logo URL")
    home_score: int | None = Field(None, description="Home score")
    away_score: int | None = Field(None, description="Away score")
    home_odds: float | None = Field(None, description="Home odds")
    draw_odds: float | None = Field(None, description="Draw odds")
    away_odds: float | None = Field(None, description="Away odds")

    class Config:
        from_attributes = True


class TeamInFixture(BaseModel):
    """Team information in fixture detail."""

    team_id: int = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    display_name: str = Field(..., description="Team display name")
    logo_url: str | None = Field(None, description="Team logo URL")
    score: int | None = Field(None, description="Team score")
    is_winner: bool | None = Field(None, description="Whether team won")


class FixtureDetailResponse(BaseModel):
    """Detailed fixture response with team information."""

    id: int = Field(..., description="Fixture database ID")
    event_id: int = Field(..., description="ESPN event ID")
    season_type: int = Field(..., description="Season type identifier")
    league_id: int = Field(..., description="League ID")
    match_date: datetime = Field(..., description="Match date and time")
    venue_id: int | None = Field(None, description="Venue ID")
    attendance: int | None = Field(None, description="Match attendance")
    home_team: TeamInFixture = Field(..., description="Home team details")
    away_team: TeamInFixture = Field(..., description="Away team details")
    home_team_shootout_score: int | None = Field(None, description="Home team shootout score")
    away_team_shootout_score: int | None = Field(None, description="Away team shootout score")
    status_id: int = Field(..., description="Match status ID")
    update_time: datetime | None = Field(None, description="Last update timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")
