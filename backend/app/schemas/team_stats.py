"""Team statistics schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ComputedStatsBase(BaseModel):
    """Base schema for computed stats."""

    # Overall stats
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    goals_scored_avg: Decimal
    goals_conceded_avg: Decimal
    clean_sheets: int
    clean_sheet_pct: Decimal
    failed_to_score: int
    failed_to_score_pct: Decimal
    points: int
    points_per_game: Decimal

    # Home stats
    home_matches: int
    home_wins: int
    home_draws: int
    home_losses: int
    home_goals_scored_avg: Decimal
    home_goals_conceded_avg: Decimal

    # Away stats
    away_matches: int
    away_wins: int
    away_draws: int
    away_losses: int
    away_goals_scored_avg: Decimal
    away_goals_conceded_avg: Decimal

    # Form (last 5 games)
    form_last5_wins: int
    form_last5_draws: int
    form_last5_losses: int
    form_last5_points: int
    form_last5_goals_scored: int
    form_last5_goals_conceded: int

    # Form (last 10 games)
    form_last10_wins: int
    form_last10_draws: int
    form_last10_losses: int
    form_last10_points: int


class ComputedStatsResponse(ComputedStatsBase):
    """Response schema for computed stats."""

    id: int
    team_id: int
    season_type: int
    computed_at: datetime

    model_config = ConfigDict(from_attributes=True)
