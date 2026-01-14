"""Team schemas for API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class TeamResponse(BaseModel):
    """Team response schema."""

    id: int = Field(..., description="Team database ID")
    team_id: int = Field(..., description="ESPN team ID")
    location: str | None = Field(None, description="Team location/city")
    name: str = Field(..., description="Team name")
    abbreviation: str | None = Field(None, description="Team abbreviation")
    display_name: str = Field(..., description="Full display name")
    short_display_name: str | None = Field(None, description="Short display name")
    color: str | None = Field(None, description="Primary team color (hex)")
    alternate_color: str | None = Field(None, description="Alternate team color (hex)")
    logo_url: str | None = Field(None, description="Team logo URL")
    venue_id: int | None = Field(None, description="Home venue ID")
    slug: str | None = Field(None, description="Team URL slug")
    created_at: datetime = Field(..., description="Record creation timestamp")

    class Config:
        from_attributes = True


class TeamStatsResponse(BaseModel):
    """Team statistics response schema."""

    id: int = Field(..., description="Stats record ID")
    season_type: int = Field(..., description="Season type identifier")
    event_id: int = Field(..., description="Match/fixture ID")
    team_id: int = Field(..., description="Team ID")
    team_order: int | None = Field(None, description="Team order in match (1=home, 2=away)")
    possession_pct: float | None = Field(None, description="Possession percentage")
    fouls_committed: float | None = Field(None, description="Fouls committed")
    yellow_cards: float | None = Field(None, description="Yellow cards")
    red_cards: float | None = Field(None, description="Red cards")
    offsides: float | None = Field(None, description="Offsides")
    won_corners: float | None = Field(None, description="Corners won")
    saves: float | None = Field(None, description="Goalkeeper saves")
    total_shots: float | None = Field(None, description="Total shots")
    shots_on_target: float | None = Field(None, description="Shots on target")
    shot_pct: float | None = Field(None, description="Shot accuracy percentage")
    penalty_kick_goals: float | None = Field(None, description="Penalty goals")
    penalty_kick_shots: float | None = Field(None, description="Penalty attempts")
    accurate_passes: float | None = Field(None, description="Accurate passes")
    total_passes: float | None = Field(None, description="Total passes")
    pass_pct: float | None = Field(None, description="Pass accuracy percentage")
    accurate_crosses: float | None = Field(None, description="Accurate crosses")
    total_crosses: float | None = Field(None, description="Total crosses")
    cross_pct: float | None = Field(None, description="Cross accuracy percentage")
    total_long_balls: float | None = Field(None, description="Total long balls")
    accurate_long_balls: float | None = Field(None, description="Accurate long balls")
    longball_pct: float | None = Field(None, description="Long ball accuracy percentage")
    blocked_shots: float | None = Field(None, description="Shots blocked")
    effective_tackles: float | None = Field(None, description="Effective tackles")
    total_tackles: float | None = Field(None, description="Total tackles")
    tackle_pct: float | None = Field(None, description="Tackle success percentage")
    interceptions: float | None = Field(None, description="Interceptions")
    effective_clearance: float | None = Field(None, description="Effective clearances")
    total_clearance: float | None = Field(None, description="Total clearances")
    update_time: datetime | None = Field(None, description="Last update timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")

    class Config:
        from_attributes = True


class TeamFormMatch(BaseModel):
    """Single match in team form history."""

    event_id: int = Field(..., description="Match ID")
    match_date: datetime = Field(..., description="Match date")
    opponent_id: int = Field(..., description="Opponent team ID")
    opponent_name: str = Field(..., description="Opponent team name")
    is_home: bool = Field(..., description="Whether team played at home")
    team_score: int | None = Field(None, description="Team's score")
    opponent_score: int | None = Field(None, description="Opponent's score")
    result: str | None = Field(None, description="Match result (W/D/L)")


class TeamFormResponse(BaseModel):
    """Team form response with recent matches."""

    team_id: int = Field(..., description="Team ID")
    team_name: str = Field(..., description="Team name")
    matches: list[TeamFormMatch] = Field(..., description="Recent matches")
    wins: int = Field(..., description="Number of wins")
    draws: int = Field(..., description="Number of draws")
    losses: int = Field(..., description="Number of losses")
    goals_for: int = Field(..., description="Goals scored")
    goals_against: int = Field(..., description="Goals conceded")
    form_string: str = Field(..., description="Form string (e.g., 'WWDLW')")
