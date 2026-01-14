"""Backtest service for evaluating filter strategies against historical data."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest_result import BacktestResult
from app.models.filter import Filter
from app.models.fixture import Fixture
from app.schemas.backtest import (
    BacktestAnalytics,
    BacktestRequest,
    BacktestResponse,
    BetType,
    DrawdownInfo,
    EnhancedBacktestResponse,
    MonthlyBreakdown,
    ProfitPoint,
    StreakInfo,
)
from app.services.filter_engine import FilterEngine


class BacktestService:
    """Service for running backtests on filter strategies."""

    # Cache TTL in hours
    CACHE_TTL_HOURS = 24

    def __init__(self, db: AsyncSession):
        self.db = db
        self.filter_engine = FilterEngine(db)

    async def run_backtest(
        self, filter_obj: Filter, request: BacktestRequest, include_analytics: bool = False
    ) -> BacktestResponse | EnhancedBacktestResponse:
        """
        Run a backtest for a filter against historical data.

        Args:
            filter_obj: Filter to backtest
            request: Backtest parameters
            include_analytics: Whether to include detailed analytics

        Returns:
            BacktestResponse or EnhancedBacktestResponse with results
        """
        # Check for cached result
        cached_result = await self._get_cached_result(
            filter_obj.id, request.bet_type, request.seasons
        )
        if cached_result and not include_analytics:
            return BacktestResponse(
                filter_id=filter_obj.id,
                bet_type=cached_result.bet_type,
                seasons=self._parse_seasons(cached_result.seasons),
                total_matches=cached_result.total_matches,
                wins=cached_result.wins,
                losses=cached_result.losses,
                pushes=cached_result.pushes,
                win_rate=cached_result.win_rate,
                total_profit=cached_result.total_profit,
                roi_percentage=cached_result.roi_percentage,
                avg_odds=cached_result.avg_odds,
                cached=True,
                run_at=cached_result.run_at,
            )

        # Get matching fixtures for the filter
        fixtures = await self._get_historical_fixtures(filter_obj.rules, request.seasons)  # type: ignore[arg-type]

        # Evaluate bets
        results = self._evaluate_bets(fixtures, request.bet_type, request.stake)

        # Calculate metrics
        response = self._calculate_metrics(filter_obj.id, request, results)

        # Add analytics if requested
        if include_analytics:
            analytics = self._generate_analytics(results, fixtures)
            enhanced_response = EnhancedBacktestResponse(
                **response.model_dump(),
                analytics=analytics,
            )
            return enhanced_response

        # Cache the result
        await self._cache_result(filter_obj.id, request, response)

        return response

    async def _get_cached_result(
        self, filter_id: int, bet_type: BetType, seasons: list[int]
    ) -> BacktestResult | None:
        """Get cached backtest result if valid."""
        seasons_str = ",".join(str(s) for s in sorted(seasons))

        result = await self.db.execute(
            select(BacktestResult).where(
                and_(
                    BacktestResult.filter_id == filter_id,
                    BacktestResult.bet_type == bet_type.value,
                    BacktestResult.seasons == seasons_str,
                    BacktestResult.expires_at > datetime.utcnow(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_historical_fixtures(
        self, rules: list[dict[str, Any]], seasons: list[int]
    ) -> list[Fixture]:
        """Get historical fixtures matching filter rules."""
        # Build query for finished matches in specified seasons
        query = select(Fixture).where(
            and_(
                Fixture.status_id == 28,  # Full Time
                Fixture.season_type.in_(seasons),
            )
        )

        # Apply filter rules
        for rule in rules:
            condition = self.filter_engine._build_condition(
                rule["field"], rule["operator"], rule["value"]
            )
            if condition is not None:
                query = query.where(condition)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _evaluate_bets(
        self, fixtures: list[Fixture], bet_type: BetType, stake: float
    ) -> list[dict[str, Any]]:
        """Evaluate bet outcomes for each fixture."""
        results = []

        for fixture in fixtures:
            outcome = self._evaluate_single_bet(fixture, bet_type)
            results.append({
                "fixture_id": fixture.id,
                "outcome": outcome,  # "win", "loss", or "push"
                "stake": stake,
                "profit": self._calculate_profit(outcome, stake),
            })

        return results

    def _evaluate_single_bet(self, fixture: Fixture, bet_type: BetType) -> str:
        """
        Evaluate a single bet outcome.

        Returns: "win", "loss", or "push"
        """
        home_score = fixture.home_team_score
        away_score = fixture.away_team_score

        # Handle missing scores
        if home_score is None or away_score is None:
            return "push"

        total_goals = home_score + away_score

        if bet_type == BetType.HOME_WIN:
            return "win" if home_score > away_score else "loss"

        elif bet_type == BetType.AWAY_WIN:
            return "win" if away_score > home_score else "loss"

        elif bet_type == BetType.DRAW:
            return "win" if home_score == away_score else "loss"

        elif bet_type == BetType.OVER_2_5:
            return "win" if total_goals > 2.5 else "loss"

        elif bet_type == BetType.UNDER_2_5:
            return "win" if total_goals < 2.5 else "loss"

        return "push"

    def _calculate_profit(self, outcome: str, stake: float) -> float:
        """
        Calculate profit for a bet outcome.

        Using flat stake with assumed odds of 2.0 (even money) for simplicity.
        In a real system, this would use actual odds data.
        """
        assumed_odds = 2.0

        if outcome == "win":
            return stake * (assumed_odds - 1)  # Net profit
        elif outcome == "loss":
            return -stake
        else:  # push
            return 0.0

    def _calculate_metrics(
        self,
        filter_id: int,
        request: BacktestRequest,
        results: list[dict[str, Any]],
    ) -> BacktestResponse:
        """Calculate backtest metrics from results."""
        total_matches = len(results)
        wins = sum(1 for r in results if r["outcome"] == "win")
        losses = sum(1 for r in results if r["outcome"] == "loss")
        pushes = sum(1 for r in results if r["outcome"] == "push")

        # Calculate win rate (excluding pushes)
        evaluated = wins + losses
        win_rate = (wins / evaluated * 100) if evaluated > 0 else 0.0

        # Calculate total profit and ROI
        total_profit = sum(r["profit"] for r in results)
        total_staked = sum(r["stake"] for r in results if r["outcome"] != "push")
        roi_percentage = (total_profit / total_staked * 100) if total_staked > 0 else 0.0

        return BacktestResponse(
            filter_id=filter_id,
            bet_type=request.bet_type.value,
            seasons=request.seasons,
            total_matches=total_matches,
            wins=wins,
            losses=losses,
            pushes=pushes,
            win_rate=round(win_rate, 2),
            total_profit=round(total_profit, 2),
            roi_percentage=round(roi_percentage, 2),
            avg_odds=2.0,  # Assumed odds
            cached=False,
            run_at=datetime.utcnow(),
        )

    async def _cache_result(
        self, filter_id: int, request: BacktestRequest, response: BacktestResponse
    ) -> None:
        """Cache backtest result."""
        # Delete any existing cache for this filter/bet_type/seasons combo
        seasons_str = ",".join(str(s) for s in sorted(request.seasons))

        await self.db.execute(
            delete(BacktestResult).where(
                and_(
                    BacktestResult.filter_id == filter_id,
                    BacktestResult.bet_type == request.bet_type.value,
                    BacktestResult.seasons == seasons_str,
                )
            )
        )

        # Create new cache entry
        cache_entry = BacktestResult(
            filter_id=filter_id,
            bet_type=request.bet_type.value,
            seasons=seasons_str,
            total_matches=response.total_matches,
            wins=response.wins,
            losses=response.losses,
            pushes=response.pushes,
            win_rate=response.win_rate,
            total_profit=response.total_profit,
            roi_percentage=response.roi_percentage,
            avg_odds=response.avg_odds,
            run_at=response.run_at,
            expires_at=datetime.utcnow() + timedelta(hours=self.CACHE_TTL_HOURS),
        )

        self.db.add(cache_entry)
        await self.db.commit()

    def _parse_seasons(self, seasons_str: str) -> list[int]:
        """Parse comma-separated seasons string to list."""
        return [int(s) for s in seasons_str.split(",")]

    def _generate_analytics(
        self, results: list[dict[str, Any]], fixtures: list[Fixture]
    ) -> BacktestAnalytics:
        """Generate detailed analytics from backtest results."""
        streaks = self.calculate_streaks(results)
        monthly = self.calculate_monthly_breakdown(results, fixtures)
        drawdown = self.calculate_drawdown(results)
        profit_curve = self.generate_profit_curve(results, fixtures)

        return BacktestAnalytics(
            streaks=streaks,
            monthly_breakdown=monthly,
            drawdown=drawdown,
            profit_curve=profit_curve,
        )

    def calculate_streaks(self, results: list[dict[str, Any]]) -> StreakInfo:
        """Calculate winning and losing streaks.

        Args:
            results: List of bet results

        Returns:
            StreakInfo with streak statistics
        """
        if not results:
            return StreakInfo(
                current_streak=0,
                longest_winning_streak=0,
                longest_losing_streak=0,
            )

        current_streak = 0
        longest_winning_streak = 0
        longest_losing_streak = 0
        temp_win_streak = 0
        temp_loss_streak = 0

        for result in results:
            outcome = result["outcome"]

            if outcome == "win":
                temp_win_streak += 1
                temp_loss_streak = 0
                current_streak = temp_win_streak
                longest_winning_streak = max(longest_winning_streak, temp_win_streak)

            elif outcome == "loss":
                temp_loss_streak += 1
                temp_win_streak = 0
                current_streak = -temp_loss_streak
                longest_losing_streak = max(longest_losing_streak, temp_loss_streak)

            # Pushes don't affect streaks

        return StreakInfo(
            current_streak=current_streak,
            longest_winning_streak=longest_winning_streak,
            longest_losing_streak=longest_losing_streak,
        )

    def calculate_monthly_breakdown(
        self, results: list[dict[str, Any]], fixtures: list[Fixture]
    ) -> list[MonthlyBreakdown]:
        """Calculate monthly performance breakdown.

        Args:
            results: List of bet results
            fixtures: List of fixtures

        Returns:
            List of MonthlyBreakdown objects
        """
        if not results or not fixtures:
            return []

        # Create fixture lookup
        fixture_map = {f.id: f for f in fixtures}

        # Group results by month
        monthly_data: dict[str, dict[str, Any]] = {}

        for result in results:
            fixture = fixture_map.get(result["fixture_id"])
            if not fixture or not fixture.match_date:
                continue

            month_key = fixture.match_date.strftime("%Y-%m")

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "matches": 0,
                    "wins": 0,
                    "losses": 0,
                    "profit": 0.0,
                }

            monthly_data[month_key]["matches"] += 1
            monthly_data[month_key]["profit"] += result["profit"]

            if result["outcome"] == "win":
                monthly_data[month_key]["wins"] += 1
            elif result["outcome"] == "loss":
                monthly_data[month_key]["losses"] += 1

        # Convert to list of MonthlyBreakdown
        breakdown = []
        for month, data in sorted(monthly_data.items()):
            evaluated = data["wins"] + data["losses"]
            win_rate = (data["wins"] / evaluated * 100) if evaluated > 0 else 0.0

            breakdown.append(
                MonthlyBreakdown(
                    month=month,
                    matches=data["matches"],
                    wins=data["wins"],
                    losses=data["losses"],
                    profit=round(data["profit"], 2),
                    win_rate=round(win_rate, 2),
                )
            )

        return breakdown

    def calculate_drawdown(self, results: list[dict[str, Any]]) -> DrawdownInfo:
        """Calculate drawdown statistics.

        Args:
            results: List of bet results

        Returns:
            DrawdownInfo with drawdown statistics
        """
        if not results:
            return DrawdownInfo(
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                current_drawdown=0.0,
                peak_balance=0.0,
            )

        balance = 0.0
        peak_balance = 0.0
        max_drawdown = 0.0
        current_drawdown = 0.0

        for result in results:
            balance += result["profit"]

            # Update peak
            if balance > peak_balance:
                peak_balance = balance
                current_drawdown = 0.0
            else:
                current_drawdown = peak_balance - balance
                max_drawdown = max(max_drawdown, current_drawdown)

        # Calculate percentage drawdown
        max_drawdown_pct = (
            (max_drawdown / peak_balance * 100) if peak_balance > 0 else 0.0
        )

        return DrawdownInfo(
            max_drawdown=round(max_drawdown, 2),
            max_drawdown_pct=round(max_drawdown_pct, 2),
            current_drawdown=round(current_drawdown, 2),
            peak_balance=round(peak_balance, 2),
        )

    def generate_profit_curve(
        self, results: list[dict[str, Any]], fixtures: list[Fixture]
    ) -> list[ProfitPoint]:
        """Generate profit curve data points.

        Args:
            results: List of bet results
            fixtures: List of fixtures

        Returns:
            List of ProfitPoint objects (max 1000 points)
        """
        if not results:
            return []

        # Create fixture lookup
        fixture_map = {f.id: f for f in fixtures}

        cumulative_profit = 0.0
        profit_points = []

        for idx, result in enumerate(results, 1):
            cumulative_profit += result["profit"]
            fixture = fixture_map.get(result["fixture_id"])

            profit_points.append(
                ProfitPoint(
                    match_number=idx,
                    cumulative_profit=round(cumulative_profit, 2),
                    date=fixture.match_date if fixture else None,
                )
            )

        # Downsample if too many points (keep every nth point)
        if len(profit_points) > 1000:
            step = len(profit_points) // 1000
            profit_points = profit_points[::step][:1000]

        return profit_points

    async def invalidate_cache(self, filter_id: int) -> None:
        """Invalidate all cached results for a filter."""
        await self.db.execute(
            delete(BacktestResult).where(BacktestResult.filter_id == filter_id)
        )
        await self.db.commit()
