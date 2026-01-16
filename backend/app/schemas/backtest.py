"""Backtest schemas for request/response validation.

This module contains schemas for backtesting filter strategies against
historical match data. Includes support for real odds data and advanced
metrics like Kelly Criterion and Expected Value.
"""

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


class OddsStats(BaseModel):
    """Statistics about odds used in backtest."""

    avg_odds: float = Field(..., description="Average odds across all bets")
    min_odds: float = Field(..., description="Minimum odds encountered")
    max_odds: float = Field(..., description="Maximum odds encountered")
    median_odds: float | None = Field(None, description="Median odds")
    std_dev: float | None = Field(None, description="Standard deviation of odds")
    has_real_odds: bool = Field(
        default=False, description="Whether real historical odds were used"
    )
    coverage_pct: float = Field(
        default=0.0, description="Percentage of matches with odds data"
    )


class BacktestResponse(BaseModel):
    """Schema for backtest response.

    Contains the core metrics for evaluating a filter strategy's performance.
    """

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
    odds_stats: OddsStats | None = Field(
        None, description="Detailed odds statistics (if odds available)"
    )

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


class KellyCriterion(BaseModel):
    """Kelly Criterion calculation for optimal stake sizing.

    The Kelly Criterion maximizes expected logarithmic growth of bankroll.
    Formula: Kelly % = W - (1-W)/Odds

    Where:
        W = probability of winning (win rate)
        Odds = decimal odds
    """

    kelly_fraction: float = Field(
        ..., ge=0, le=1, description="Full Kelly fraction (0-1)"
    )
    half_kelly: float = Field(
        ..., ge=0, le=1, description="Half Kelly (more conservative)"
    )
    quarter_kelly: float = Field(
        ..., ge=0, le=1, description="Quarter Kelly (most conservative)"
    )
    recommended_stake: float = Field(
        ..., description="Recommended stake as percentage of bankroll"
    )
    is_positive_edge: bool = Field(
        ..., description="Whether strategy has positive expected value"
    )
    kelly_description: str = Field(
        ..., description="Human-readable interpretation of Kelly result"
    )


class ConfidenceInterval(BaseModel):
    """Statistical confidence interval for a metric."""

    lower: float = Field(..., description="Lower bound of confidence interval")
    upper: float = Field(..., description="Upper bound of confidence interval")
    confidence_level: float = Field(
        ..., description="Confidence level (e.g., 0.95 for 95%)"
    )


class StatisticalSignificance(BaseModel):
    """Statistical significance test results."""

    p_value: float = Field(
        ..., description="P-value from statistical test"
    )
    is_significant: bool = Field(
        ..., description="Whether result is statistically significant (p < 0.05)"
    )
    significance_level: float = Field(
        default=0.05, description="Significance threshold used"
    )
    effect_size: float | None = Field(
        None, description="Cohen's h effect size for win rate difference"
    )
    interpretation: str = Field(
        ..., description="Human-readable interpretation of significance test"
    )


class ExpectedValue(BaseModel):
    """Expected Value analysis for betting strategy."""

    expected_value_per_bet: float = Field(
        ..., description="Expected value in stake units per bet"
    )
    expected_value_percentage: float = Field(
        ..., description="Expected value as percentage of stake"
    )
    total_expected_profit: float = Field(
        ..., description="Expected total profit over all bets"
    )
    edge_over_breakeven: float = Field(
        ..., description="Edge over breakeven point"
    )
    probability_of_profit: float = Field(
        ..., description="Estimated probability of being profitable"
    )


class AdvancedMetrics(BaseModel):
    """Advanced statistical metrics for backtest results."""

    kelly_criterion: KellyCriterion
    expected_value: ExpectedValue
    win_rate_confidence_interval: ConfidenceInterval
    statistical_significance: StatisticalSignificance
    sample_size_sufficient: bool = Field(
        ..., description="Whether sample size is sufficient for statistical validity"
    )
    minimum_sample_recommended: int = Field(
        ..., description="Minimum matches recommended for statistical significance"
    )
    risk_of_ruin: float | None = Field(
        None, description="Estimated risk of ruin with infinite play"
    )
    sharpe_ratio: float | None = Field(
        None, description="Risk-adjusted return metric"
    )
    sortino_ratio: float | None = Field(
        None, description="Downside risk-adjusted return metric"
    )


class EnhancedBacktestResponse(BacktestResponse):
    """Enhanced backtest response with analytics and advanced metrics."""

    analytics: BacktestAnalytics | None = Field(
        None, description="Detailed analytics (optional)"
    )
    advanced_metrics: AdvancedMetrics | None = Field(
        None, description="Advanced statistical metrics (Kelly Criterion, EV, etc.)"
    )
