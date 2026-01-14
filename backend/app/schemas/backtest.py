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


class StreakInfo(BaseModel):
    """Streak information for wins/losses."""

    current_streak: int = Field(..., description="Current streak (positive=wins, negative=losses)")
    longest_winning_streak: int = Field(..., description="Longest winning streak")
    longest_losing_streak: int = Field(..., description="Longest losing streak")


class MonthlyBreakdown(BaseModel):
    """Monthly performance breakdown."""

    month: str = Field(..., description="Month in YYYY-MM format")
    matches: int = Field(..., description="Number of matches")
    wins: int = Field(..., description="Number of wins")
    losses: int = Field(..., description="Number of losses")
    profit: float = Field(..., description="Profit for the month")
    win_rate: float = Field(..., description="Win rate percentage")


class DrawdownInfo(BaseModel):
    """Drawdown analysis."""

    max_drawdown: float = Field(..., description="Maximum drawdown in stake units")
    max_drawdown_pct: float = Field(..., description="Maximum drawdown as percentage")
    current_drawdown: float = Field(..., description="Current drawdown")
    peak_balance: float = Field(..., description="Peak balance achieved")


class ProfitPoint(BaseModel):
    """Single point in profit curve."""

    match_number: int = Field(..., description="Sequential match number")
    cumulative_profit: float = Field(..., description="Cumulative profit at this point")
    date: datetime | None = Field(None, description="Match date")


class BacktestAnalytics(BaseModel):
    """Enhanced analytics for backtest results."""

    streaks: StreakInfo
    monthly_breakdown: list[MonthlyBreakdown]
    drawdown: DrawdownInfo
    profit_curve: list[ProfitPoint] = Field(
        ..., max_length=1000, description="Profit curve data (max 1000 points)"
    )


class EnhancedBacktestResponse(BacktestResponse):
    """Enhanced backtest response with analytics."""

    analytics: BacktestAnalytics | None = Field(
        None, description="Detailed analytics (optional)"
    )
