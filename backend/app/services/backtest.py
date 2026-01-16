"""Backtest service for evaluating filter strategies against historical data."""

from datetime import datetime, timedelta
from math import asin, exp, sqrt as math_sqrt
from statistics import mean, median, stdev
from typing import Any

from sqlalchemy import and_, delete, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest_result import BacktestResult
from app.models.filter import Filter
from app.models.fixture import Fixture
from app.schemas.backtest import (
    AdvancedMetrics,
    BacktestAnalytics,
    BacktestRequest,
    BacktestResponse,
    BetType,
    ConfidenceInterval,
    DrawdownInfo,
    EnhancedBacktestResponse,
    ExpectedValue,
    KellyCriterion,
    MonthlyBreakdown,
    OddsStats,
    ProfitPoint,
    StatisticalSignificance,
    StreakInfo,
)
from app.services.filter_engine import FilterEngine


class BacktestService:
    """Service for running backtests on filter strategies."""

    CACHE_TTL_HOURS = 24

    def __init__(self, db: AsyncSession):
        self.db = db
        self.filter_engine = FilterEngine(db)

    async def run_backtest(
        self, filter_obj: Filter, request: BacktestRequest, include_analytics: bool = False
    ) -> BacktestResponse:
        """Run a backtest for a filter against historical data."""
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
                odds_stats=None,
            )

        rules_raw = filter_obj.rules
        if isinstance(rules_raw, dict) and "rules" in rules_raw:
            rules_list = rules_raw["rules"]
        elif isinstance(rules_raw, dict):
            rules_list = list(rules_raw.values())
        else:
            rules_list = rules_raw

        fixtures = await self._get_historical_fixtures(rules_list, request.seasons)

        results = self._evaluate_bets(fixtures, request.bet_type, request.stake)

        response = self._calculate_metrics(filter_obj.id, request, results)

        if include_analytics:
            analytics = self._generate_analytics(results, fixtures)
            avg_odds = response.avg_odds if response.avg_odds else 2.0
            advanced_metrics = self.calculate_advanced_metrics(
                win_rate=response.win_rate,
                avg_odds=avg_odds,
                total_bets=response.wins + response.losses,
                roi=response.roi_percentage,
            )
            enhanced_response = EnhancedBacktestResponse(
                **response.model_dump(),
                analytics=analytics,
                advanced_metrics=advanced_metrics,
            )
            return enhanced_response

        await self._cache_result(filter_obj.id, request, response)

        return response

    async def run_enhanced_pre_match_backtest(
        self,
        filter_obj: Filter,
        bet_type: BetType,
        seasons: list[int],
        include_analytics: bool = True,
    ) -> EnhancedBacktestResponse:
        """Run enhanced pre-match backtest with detailed analytics."""
        request = BacktestRequest(bet_type=bet_type, seasons=seasons)
        result = await self.run_backtest(filter_obj, request, include_analytics=include_analytics)
        if isinstance(result, EnhancedBacktestResponse):
            return result
        return EnhancedBacktestResponse(**result.model_dump())

    async def get_quick_pre_match_analytics(
        self,
        filter_obj: Filter,
        seasons: list[int] | None = None,
    ) -> dict[str, Any]:
        """Get quick pre-match analytics for a filter."""
        seasons_to_use = seasons or [2024, 2025]
        request = BacktestRequest(bet_type=BetType.OVER_2_5, seasons=seasons_to_use)
        result = await self.run_backtest(filter_obj, request, include_analytics=True)

        analytics_data: dict[str, Any] = {}
        if isinstance(result, EnhancedBacktestResponse) and result.analytics:
            analytics_data = {
                "performance_summary": {
                    "win_rate": result.win_rate,
                    "roi": result.roi_percentage,
                    "total_matches": result.total_matches,
                },
                "trends": [m.model_dump() for m in result.analytics.monthly_breakdown[-3:]]
                if result.analytics.monthly_breakdown else [],
                "risk_metrics": result.analytics.drawdown.model_dump(),
            }

        return analytics_data

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
        query = select(Fixture).where(
            and_(
                Fixture.status_id == 28,
                extract('year', Fixture.match_date).in_(seasons),
            )
        )

        for rule in rules:
            condition = self.filter_engine._build_condition(
                rule["field"], rule["operator"], rule["value"]
            )
            if condition is not None:
                query = query.where(condition)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _get_fixture_odds(self, fixture: Fixture, bet_type: BetType) -> float:
        """Get odds for a fixture based on bet type.

        Returns real odds if available, otherwise falls back to default 2.0.
        """
        features = fixture.features_metadata or {}
        odds_data = features.get("odds")

        if odds_data:
            if bet_type == BetType.HOME_WIN:
                return odds_data.get("home_odds", 2.0)
            elif bet_type == BetType.AWAY_WIN:
                return odds_data.get("away_odds", 2.0)
            elif bet_type == BetType.DRAW:
                return odds_data.get("draw_odds", 3.0)
            elif bet_type in (BetType.OVER_2_5, BetType.UNDER_2_5):
                over_odds = odds_data.get("over_2_5_odds")
                if over_odds:
                    return over_odds

        return 2.0  # Default odds if not available

    def _evaluate_bets(
        self, fixtures: list[Fixture], bet_type: BetType, stake: float
    ) -> list[dict[str, Any]]:
        """Evaluate bet outcomes for each fixture with real odds."""
        results = []

        for fixture in fixtures:
            outcome = self._evaluate_single_bet(fixture, bet_type)
            odds = self._get_fixture_odds(fixture, bet_type)

            results.append({
                "fixture_id": fixture.id,
                "outcome": outcome,
                "stake": stake,
                "odds": odds,
                "profit": self._calculate_profit(outcome, stake, odds),
                "match_date": fixture.match_date,
            })

        return results

    def _evaluate_single_bet(self, fixture: Fixture, bet_type: BetType) -> str:
        """Evaluate a single bet outcome.

        Returns: "win", "loss", or "push"
        """
        home_score = fixture.home_team_score
        away_score = fixture.away_team_score

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

    def _calculate_profit(self, outcome: str, stake: float, odds: float) -> float:
        """Calculate profit using real odds.

        Args:
            outcome: "win", "loss", or "push"
            stake: Amount wagered
            odds: Decimal odds for the bet
        """
        if outcome == "win":
            return stake * (odds - 1)
        elif outcome == "loss":
            return -stake
        return 0.0

    def _calculate_odds_stats(self, results: list[dict[str, Any]]) -> OddsStats:
        """Calculate statistics about odds used in the backtest."""
        odds_values = [r["odds"] for r in results if r["outcome"] != "push"]
        fixtures_with_odds = sum(
            1 for r in results
            if r.get("odds", 2.0) != 2.0 or r.get("outcome") != "push"
        )

        if not odds_values:
            return OddsStats(
                avg_odds=2.0,
                min_odds=2.0,
                max_odds=2.0,
                median_odds=None,
                std_dev=None,
                has_real_odds=False,
                coverage_pct=0.0,
            )

        has_real_odds = any(o != 2.0 for o in odds_values)
        avg_odds = mean(odds_values)
        min_odds = min(odds_values)
        max_odds = max(odds_values)
        median_odds = median(odds_values)
        std_dev = stdev(odds_values) if len(odds_values) > 1 else None
        coverage_pct = (fixtures_with_odds / len(results)) * 100 if results else 0.0

        return OddsStats(
            avg_odds=round(avg_odds, 3),
            min_odds=round(min_odds, 3),
            max_odds=round(max_odds, 3),
            median_odds=round(median_odds, 3) if median_odds else None,
            std_dev=round(std_dev, 3) if std_dev else None,
            has_real_odds=has_real_odds,
            coverage_pct=round(coverage_pct, 2),
        )

    def _calculate_metrics(
        self,
        filter_id: int,
        request: BacktestRequest,
        results: list[dict[str, Any]],
    ) -> BacktestResponse:
        """Calculate backtest metrics from results with real odds."""
        total_matches = len(results)
        wins = sum(1 for r in results if r["outcome"] == "win")
        losses = sum(1 for r in results if r["outcome"] == "loss")
        pushes = sum(1 for r in results if r["outcome"] == "push")

        evaluated = wins + losses
        win_rate = (wins / evaluated * 100) if evaluated > 0 else 0.0

        total_profit = sum(r["profit"] for r in results)
        total_staked = sum(r["stake"] for r in results if r["outcome"] != "push")
        roi_percentage = (total_profit / total_staked * 100) if total_staked > 0 else 0.0

        odds_stats = self._calculate_odds_stats(results)
        avg_odds = odds_stats.avg_odds if odds_stats.has_real_odds else 2.0

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
            avg_odds=avg_odds,
            cached=False,
            run_at=datetime.utcnow(),
            odds_stats=odds_stats,
        )

    async def _cache_result(
        self, filter_id: int, request: BacktestRequest, response: BacktestResponse
    ) -> None:
        """Cache backtest result."""
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

    def calculate_kelly_criterion(
        self, win_rate: float, avg_odds: float, total_bets: int
    ) -> KellyCriterion:
        """Calculate Kelly Criterion for optimal stake sizing.

        Kelly Formula: Kelly % = W - (1-W)/Odds

        Where:
            W = probability of winning (as decimal, e.g., 0.52 for 52%)
            Odds = decimal odds

        Args:
            win_rate: Win rate as percentage (0-100)
            avg_odds: Average decimal odds
            total_bets: Total number of bets placed

        Returns:
            KellyCriterion with calculated values
        """
        W = win_rate / 100.0
        odds = avg_odds

        expected_value = (W * odds) - 1

        full_kelly = W - ((1 - W) / odds)

        if expected_value <= 0:
            full_kelly = max(0.0, -abs(full_kelly))
        else:
            full_kelly = max(0.0, min(1.0, full_kelly))

        half_kelly = full_kelly / 2 if full_kelly > 0 else 0.0
        quarter_kelly = full_kelly / 4 if full_kelly > 0 else 0.0

        is_positive_edge = expected_value > 0

        if expected_value > 0.05:
            kelly_description = (
                "High Kelly - strategy shows strong positive edge. "
                "Consider using fractional Kelly for reduced volatility."
            )
        elif expected_value > 0:
            kelly_description = (
                "Moderate Kelly - positive edge detected. "
                "Fractional Kelly (1/2 or 1/4) recommended for stability."
            )
        elif expected_value == 0:
            kelly_description = (
                "No edge - at breakeven point. Kelly is zero."
            )
        else:
            kelly_description = (
                "Negative edge - Kelly is negative. "
                "Strategy does not have mathematical advantage at current odds."
            )

        return KellyCriterion(
            kelly_fraction=round(full_kelly, 4),
            half_kelly=round(half_kelly, 4),
            quarter_kelly=round(quarter_kelly, 4),
            recommended_stake=round(half_kelly * 100, 2),
            is_positive_edge=is_positive_edge,
            kelly_description=kelly_description,
        )

    def calculate_expected_value(
        self, win_rate: float, avg_odds: float, total_bets: int
    ) -> ExpectedValue:
        """Calculate Expected Value metrics.

        EV = (Win Rate * Odds - 1) per unit staked

        Args:
            win_rate: Win rate as percentage (0-100)
            avg_odds: Average decimal odds
            total_bets: Total number of bets placed

        Returns:
            ExpectedValue with calculated metrics
        """
        W = win_rate / 100.0
        odds = avg_odds

        ev_per_bet = (W * odds) - 1
        ev_percentage = ev_per_bet * 100
        total_ev = ev_per_bet * total_bets

        breakeven_rate = (1 / odds) * 100
        edge = win_rate - breakeven_rate

        if ev_per_bet > 0:
            z_score = ev_per_bet / max(0.01, (1 / total_bets) ** 0.5)
            prob_profit = 0.5 * (1 + self._erf(z_score / (2 ** 0.5)))
        else:
            prob_profit = max(0.0, 1 - (abs(ev_per_bet) / 2))

        return ExpectedValue(
            expected_value_per_bet=round(ev_per_bet, 4),
            expected_value_percentage=round(ev_percentage, 2),
            total_expected_profit=round(total_ev, 2),
            edge_over_breakeven=round(edge, 2),
            probability_of_profit=round(min(1.0, max(0.0, prob_profit)), 2),
        )

    def _erf(self, x: float) -> float:
        """Approximate error function for normal CDF calculation."""
        sign = 1 if x >= 0 else -1
        x = abs(x)
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911

        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * exp(-x * x)
        return sign * y

    def calculate_confidence_interval(
        self, win_rate: float, total_bets: int, confidence: float = 0.95
    ) -> ConfidenceInterval:
        """Calculate confidence interval for win rate.

        Uses normal approximation with standard error.

        Args:
            win_rate: Win rate as percentage (0-100)
            total_bets: Total number of bets evaluated
            confidence: Confidence level (default 0.95 for 95%)

        Returns:
            ConfidenceInterval with bounds
        """

        p = win_rate / 100.0
        n = total_bets

        if n == 0 or p == 0 or p == 1:
            return ConfidenceInterval(
                lower=win_rate, upper=win_rate, confidence_level=confidence
            )

        se = math_sqrt((p * (1 - p)) / n)
        z = self._get_z_score(confidence)

        margin = z * se * 100
        lower = max(0.0, win_rate - margin)
        upper = min(100.0, win_rate + margin)

        return ConfidenceInterval(
            lower=round(lower, 2),
            upper=round(upper, 2),
            confidence_level=confidence,
        )

    def _get_z_score(self, confidence: float) -> float:
        """Get z-score for confidence level."""
        if confidence >= 0.99:
            return 2.576
        elif confidence >= 0.95:
            return 1.96
        elif confidence >= 0.90:
            return 1.645
        return 1.96

    def calculate_statistical_significance(
        self, win_rate: float, total_bets: int, expected_win_rate: float = 50.0
    ) -> StatisticalSignificance:
        """Calculate statistical significance of win rate.

        Tests if observed win rate is significantly different from
        the expected rate (default 50% for even-money bets).

        Args:
            win_rate: Observed win rate as percentage
            total_bets: Number of bets evaluated
            expected_win_rate: Expected win rate under null hypothesis

        Returns:
            StatisticalSignificance with test results
        """

        n = total_bets
        if n < 30:
            return StatisticalSignificance(
                p_value=1.0,
                is_significant=False,
                significance_level=0.05,
                effect_size=None,
                interpretation="Insufficient sample size for statistical testing (need 30+ bets)",
            )

        p_observed = win_rate / 100.0
        p_expected = expected_win_rate / 100.0

        if p_observed == p_expected:
            return StatisticalSignificance(
                p_value=1.0,
                is_significant=False,
                significance_level=0.05,
                effect_size=0.0,
                interpretation="Win rate equals expected rate",
            )

        se = math_sqrt((p_expected * (1 - p_expected)) / n)
        if se == 0:
            return StatisticalSignificance(
                p_value=0.0,
                is_significant=True,
                significance_level=0.05,
                effect_size=1.0,
                interpretation="Perfect win rate - statistically significant",
            )

        z_score = (p_observed - p_expected) / se

        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))

        effect_size = 2 * (asin(math_sqrt(p_observed)) - asin(math_sqrt(p_expected)))

        is_significant = p_value < 0.05

        if is_significant:
            if p_observed > p_expected:
                interpretation = (
                    f"Statistically significant positive result (p={p_value:.4f}). "
                    f"Win rate {win_rate:.1f}% exceeds expected {expected_win_rate:.1f}%."
                )
            else:
                interpretation = (
                    f"Statistically significant negative result (p={p_value:.4f}). "
                    f"Win rate {win_rate:.1f}% below expected {expected_win_rate:.1f}%."
                )
        else:
            interpretation = (
                f"Result not statistically significant (p={p_value:.4f}). "
                f"Cannot conclude win rate differs from {expected_win_rate:.1f}%."
            )

        return StatisticalSignificance(
            p_value=round(p_value, 4),
            is_significant=is_significant,
            significance_level=0.05,
            effect_size=round(abs(effect_size), 3),
            interpretation=interpretation,
        )

    def _normal_cdf(self, x: float) -> float:
        """Calculate cumulative distribution function of normal distribution."""
        return 0.5 * (1 + self._erf(x / math_sqrt(2)))

    def calculate_advanced_metrics(
        self, win_rate: float, avg_odds: float, total_bets: int, roi: float
    ) -> AdvancedMetrics:
        """Calculate all advanced metrics for backtest results.

        Args:
            win_rate: Win rate as percentage (0-100)
            avg_odds: Average decimal odds
            total_bets: Total number of bets placed
            roi: Return on investment percentage

        Returns:
            AdvancedMetrics with all calculated values
        """
        kelly = self.calculate_kelly_criterion(win_rate, avg_odds, total_bets)
        ev = self.calculate_expected_value(win_rate, avg_odds, total_bets)
        ci = self.calculate_confidence_interval(win_rate, total_bets)
        significance = self.calculate_statistical_significance(win_rate, total_bets)

        min_sample = max(30, int(100 / max(0.01, (win_rate / 100) * (1 - win_rate / 100))))
        sample_sufficient = total_bets >= min_sample

        risk_of_ruin = None
        if kelly.kelly_fraction > 0:
            risk_of_ruin = max(0.0, (1 - kelly.kelly_fraction) ** total_bets)

        sharpe_ratio = None
        sortino_ratio = None
        if roi > 0 and total_bets > 0:
            returns_std = max(0.01, abs(roi) / math_sqrt(total_bets))
            sharpe_ratio = round(roi / (returns_std * math_sqrt(100)), 2) if returns_std > 0 else 0

        return AdvancedMetrics(
            kelly_criterion=kelly,
            expected_value=ev,
            win_rate_confidence_interval=ci,
            statistical_significance=significance,
            sample_size_sufficient=sample_sufficient,
            minimum_sample_recommended=min_sample,
            risk_of_ruin=round(risk_of_ruin, 4) if risk_of_ruin else None,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
        )
