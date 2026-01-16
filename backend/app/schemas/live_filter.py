"""Live filter schemas for request/response validation."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# Base rule schemas for different categories
class LiveStatsRule(BaseModel):
    """Live Stats rule (Category A) - In-game events and stats."""

    category: Literal["live_stats"] = Field(..., description="Rule category")
    metric: Literal[
        "goals", "total_goals", "corners", "total_corners",
        "shots_on_target", "total_shots_on_target", "dangerous_attacks",
        "total_dangerous_attacks", "possession", "yellow_cards",
        "total_yellow_cards", "red_cards", "total_red_cards"
    ] = Field(..., description="Live stat metric")
    target: Literal[
        "HOME", "AWAY", "EITHER", "MATCH", "FAVORITE", "FAVORITE_HOME",
        "FAVORITE_AWAY", "UNDERDOG", "UNDERDOG_HOME", "UNDERDOG_AWAY",
        "WINNING", "LOSING"
    ] = Field(..., description="Target for the stat")
    comparator: Literal["=", "!=", ">", "<", ">=", "<="] = Field(..., description="Comparison operator")
    value: float | None = Field(None, description="Value for numeric mode")
    compare_to: str | None = Field(None, description="Target for advanced mode (e.g., 'AWAY')")


class TeamStateRule(BaseModel):
    """Team State rule (Category A extension) - Win/Draw/Loss status."""

    category: Literal["team_state"] = Field(..., description="Rule category")
    team_state: Literal["WINNING", "LOSING", "DRAWING", "NOT_WINNING", "NOT_LOSING"] = Field(
        ..., description="Team state condition"
    )
    target: Literal["HOME", "AWAY", "EITHER"] = Field(..., description="Which team to check")


class OddsRule(BaseModel):
    """Odds rule (Category C) - Live and pre-match odds."""

    category: Literal["odds"] = Field(..., description="Rule category")
    market: Literal[
        "1X2", "DOUBLE_CHANCE", "OVER_UNDER", "BTTS", "CORNERS",
        "HALF_TIME_1X2", "HALF_TIME_OVER_UNDER", "HALF_TIME_BTTS"
    ] = Field(..., description="Betting market")
    selection: Literal["HOME", "DRAW", "AWAY", "OVER", "UNDER", "YES", "NO", "1X", "12", "X2"] = Field(
        ..., description="Market selection"
    )
    line: float | None = Field(None, description="Line for OU/Corners markets (e.g., 2.5)")
    comparator: Literal["=", "!=", ">", "<", ">=", "<="] = Field(..., description="Comparison operator")
    value: float = Field(..., description="Odds value to compare")


class TimingRule(BaseModel):
    """Timing rule (Category D) - Match minute filters."""

    category: Literal["timing"] = Field(..., description="Rule category")
    before_minute: int | None = Field(None, ge=1, le=120, description="Trigger before this minute")
    after_minute: int | None = Field(None, ge=1, le=120, description="Trigger after this minute")
    at_minute: int | None = Field(None, ge=1, le=120, description="Trigger at this exact minute")


class PreMatchStatsRule(BaseModel):
    """Pre-Match Stats rule (Category E) - Historical and AI probabilities."""

    category: Literal["pre_match_stats"] = Field(..., description="Rule category")
    metric: Literal[
        "avg_goals_scored", "avg_goals_conceded", "clean_sheet_pct",
        "win_pct", "draw_pct", "loss_pct", "points_per_game",
        "ai_home_win_prob", "ai_away_win_prob", "ai_draw_prob",
        "ai_over_2_5_prob", "ai_btts_prob", "historical_over_2_5_pct",
        "historical_btts_pct", "historical_1x2_home_pct"
    ] = Field(..., description="Pre-match stat metric")
    target: Literal["HOME", "AWAY", "EITHER", "MATCH"] = Field(..., description="Target for the stat")
    comparator: Literal["=", "!=", ">", "<", ">=", "<="] = Field(..., description="Comparison operator")
    value: float = Field(..., description="Value to compare")


# Union type for all live rule types
LiveRule = (
    LiveStatsRule | TeamStateRule | OddsRule | TimingRule | PreMatchStatsRule
)


class LiveFilterCreate(BaseModel):
    """Schema for creating a new live filter."""

    name: str = Field(..., min_length=1, max_length=100, description="Filter name")
    description: str | None = Field(None, max_length=500, description="Filter description")
    rules: list[LiveRule] = Field(
        ..., min_length=1, max_length=10, description="Live filter conditions (max 10)"
    )
    is_active: bool = Field(True, description="Whether filter is active")
    filter_type: Literal["live", "backtest"] = Field(..., description="Filter type")


class LiveFilterUpdate(BaseModel):
    """Schema for updating an existing live filter."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    rules: list[LiveRule] | None = Field(None, min_length=1, max_length=10)
    is_active: bool | None = None


class LiveMatchResponse(BaseModel):
    """Schema for live match response."""

    id: int
    fixture_id: int
    status: str
    minute: int
    home_score: int
    away_score: int
    live_stats: dict[str, Any]
    home_team_state: str | None
    away_team_state: str | None
    momentum: str | None
    ai_predictions: dict[str, Any] | None
    historical_stats: dict[str, Any] | None
    last_update: datetime

    model_config = {"from_attributes": True}


class LiveOddsResponse(BaseModel):
    """Schema for live odds response."""

    id: int
    fixture_id: int
    market_type: str
    selection: str
    line: float | None
    odds: float
    fetched_at: datetime

    model_config = {"from_attributes": True}


class LiveFilterResultResponse(BaseModel):
    """Schema for live filter result response with dual-stat comparison."""

    id: int
    filter_id: int
    fixture_id: int
    triggered_at: datetime
    triggered_minute: int
    notification_value: dict[str, Any]  # Stats at alert moment
    final_value: dict[str, Any] | None  # Final/current stats
    bet_result: str
    resolved_at: datetime | None
    odds_at_trigger: dict[str, Any] | None

    model_config = {"from_attributes": True}


class LiveScannerStatsResponse(BaseModel):
    """Schema for live scanner statistics."""

    active_filters: int
    live_matches: int
    alerts_today: int
    success_rate_24h: float | None
    avg_odds_today: float | None


class LiveFilterBacktestRequest(BaseModel):
    """Schema for live filter backtest request."""

    filter_id: int
    date_range: tuple[str, str] | None = Field(None, description="Date range for backtest")
    include_resolved: bool = Field(True, description="Include resolved results")


class LiveFilterBacktestResponse(BaseModel):
    """Schema for live filter backtest response."""

    filter_id: int
    total_alerts: int
    resolved_alerts: int
    wins: int
    losses: int
    pushes: int
    success_rate: float
    avg_odds: float
    roi: float
    results: list[LiveFilterResultResponse]
