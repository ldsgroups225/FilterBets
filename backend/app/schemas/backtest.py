"""Backtest schemas for request/response validation."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BetType(str, Enum):
    """Supported bet types for backtesting."""

    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"
    OVER_2_5 = "over_2_5"
    UNDER_2_5 = "under_2_5"


class BacktestRequest(BaseModel):
    """Schema for backtest request."""

    bet_type: BetType = Field(..., description="Type of bet to evaluate")
    seasons: list[int] = Field(
        default=[2024, 2025],
        min_length=1,
        max_length=5,
        description="Season years to include in backtest",
    )
    stake: float = Field(default=1.0, gt=0, description="Flat stake amount per bet")


class BacktestResponse(BaseModel):
    """Schema for backtest response."""

    filter_id: int
    bet_type: str
    seasons: list[int]
    total_matches: int = Field(..., description="Total matches evaluated")
    wins: int = Field(..., description="Number of winning bets")
    losses: int = Field(..., description="Number of losing bets")
    pushes: int = Field(default=0, description="Number of void/push bets")
    win_rate: float = Field(..., description="Win rate as percentage (0-100)")
    total_profit: float = Field(..., description="Total profit/loss in stake units")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    avg_odds: float | None = Field(None, description="Average odds (if available)")
    cached: bool = Field(default=False, description="Whether result was from cache")
    run_at: datetime = Field(..., description="When backtest was run")

    model_config = {"from_attributes": True}


class BacktestSummary(BaseModel):
    """Summary of a backtest result for listing."""

    id: int
    filter_id: int
    bet_type: str
    win_rate: float
    roi_percentage: float
    total_matches: int
    run_at: datetime

    model_config = {"from_attributes": True}
