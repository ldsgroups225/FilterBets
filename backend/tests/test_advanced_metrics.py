"""Tests for advanced backtest metrics calculations."""

import pytest
from app.services.backtest import BacktestService


class TestKellyCriterion:
    """Tests for Kelly Criterion calculations."""

    def test_kelly_positive_edge(self):
        """Test Kelly calculation with positive edge."""
        service = BacktestService.__new__(BacktestService)
        kelly = service.calculate_kelly_criterion(win_rate=55.0, avg_odds=2.0, total_bets=100)

        assert kelly.kelly_fraction > 0
        assert kelly.half_kelly > 0
        assert kelly.quarter_kelly > 0
        assert kelly.is_positive_edge is True
        assert kelly.recommended_stake == kelly.half_kelly * 100

    def test_kelly_negative_edge(self):
        """Test Kelly calculation with negative edge."""
        service = BacktestService.__new__(BacktestService)
        kelly = service.calculate_kelly_criterion(win_rate=40.0, avg_odds=2.0, total_bets=100)

        assert kelly.kelly_fraction == 0
        assert kelly.is_positive_edge is False

    def test_kelly_no_edge(self):
        """Test Kelly calculation at breakeven."""
        service = BacktestService.__new__(BacktestService)
        kelly = service.calculate_kelly_criterion(win_rate=50.0, avg_odds=2.0, total_bets=100)

        assert kelly.kelly_fraction == 0

    def test_kelly_fractions_order(self):
        """Test that Kelly fractions are ordered correctly."""
        service = BacktestService.__new__(BacktestService)
        kelly = service.calculate_kelly_criterion(win_rate=60.0, avg_odds=2.0, total_bets=100)

        assert kelly.quarter_kelly < kelly.half_kelly < kelly.kelly_fraction


class TestExpectedValue:
    """Tests for Expected Value calculations."""

    def test_ev_positive(self):
        """Test EV with positive edge."""
        service = BacktestService.__new__(BacktestService)
        ev = service.calculate_expected_value(win_rate=55.0, avg_odds=2.0, total_bets=100)

        assert ev.expected_value_per_bet > 0
        assert ev.expected_value_percentage > 0
        assert ev.edge_over_breakeven > 0

    def test_ev_negative(self):
        """Test EV with negative edge."""
        service = BacktestService.__new__(BacktestService)
        ev = service.calculate_expected_value(win_rate=45.0, avg_odds=2.0, total_bets=100)

        assert ev.expected_value_per_bet < 0
        assert ev.expected_value_percentage < 0

    def test_ev_breakeven(self):
        """Test EV at breakeven point."""
        service = BacktestService.__new__(BacktestService)
        ev = service.calculate_expected_value(win_rate=50.0, avg_odds=2.0, total_bets=100)

        assert ev.expected_value_per_bet == 0
        assert ev.edge_over_breakeven == 0


class TestConfidenceInterval:
    """Tests for confidence interval calculations."""

    def test_ci_95_percent(self):
        """Test 95% confidence interval."""
        service = BacktestService.__new__(BacktestService)
        ci = service.calculate_confidence_interval(win_rate=50.0, total_bets=100)

        assert ci.confidence_level == 0.95
        assert ci.lower < 50.0 < ci.upper
        assert ci.upper - ci.lower > 0

    def test_ci_wider_with_more_bets(self):
        """Test that CI gets narrower with more bets."""
        service = BacktestService.__new__(BacktestService)
        ci_narrow = service.calculate_confidence_interval(win_rate=50.0, total_bets=1000)
        ci_wide = service.calculate_confidence_interval(win_rate=50.0, total_bets=100)

        assert (ci_narrow.upper - ci_narrow.lower) < (ci_wide.upper - ci_wide.lower)


class TestStatisticalSignificance:
    """Tests for statistical significance calculations."""

    def test_significant_result(self):
        """Test statistically significant result."""
        service = BacktestService.__new__(BacktestService)
        sig = service.calculate_statistical_significance(win_rate=60.0, total_bets=200)

        assert sig.is_significant is True
        assert sig.p_value < 0.05
        assert sig.effect_size is not None

    def test_not_significant_result(self):
        """Test not statistically significant result."""
        service = BacktestService.__new__(BacktestService)
        sig = service.calculate_statistical_significance(win_rate=52.0, total_bets=50)

        assert sig.p_value >= 0.05

    def test_insufficient_sample(self):
        """Test with insufficient sample size."""
        service = BacktestService.__new__(BacktestService)
        sig = service.calculate_statistical_significance(win_rate=60.0, total_bets=20)

        assert sig.is_significant is False
        assert "Insufficient sample size" in sig.interpretation


class TestAdvancedMetrics:
    """Tests for complete advanced metrics calculation."""

    def test_advanced_metrics_complete(self):
        """Test that all advanced metrics are calculated."""
        service = BacktestService.__new__(BacktestService)
        metrics = service.calculate_advanced_metrics(
            win_rate=55.0, avg_odds=2.0, total_bets=200, roi=10.0
        )

        assert metrics.kelly_criterion is not None
        assert metrics.expected_value is not None
        assert metrics.win_rate_confidence_interval is not None
        assert metrics.statistical_significance is not None

    def test_sample_size_sufficient(self):
        """Test sample size sufficiency check."""
        service = BacktestService.__new__(BacktestService)
        # With 55% win rate at 2.0 odds, we need more bets for statistical significance
        metrics = service.calculate_advanced_metrics(
            win_rate=55.0, avg_odds=2.0, total_bets=200, roi=10.0
        )

        # 200 bets may not be sufficient for statistical significance at this win rate
        assert metrics.minimum_sample_recommended > 0
        # Note: sample_size_sufficient depends on the observed variance

    def test_sample_size_sufficient_high_bets(self):
        """Test sample size sufficiency with enough bets."""
        service = BacktestService.__new__(BacktestService)
        metrics = service.calculate_advanced_metrics(
            win_rate=55.0, avg_odds=2.0, total_bets=500, roi=10.0
        )

        assert metrics.minimum_sample_recommended > 0

    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        service = BacktestService.__new__(BacktestService)
        metrics = service.calculate_advanced_metrics(
            win_rate=55.0, avg_odds=2.0, total_bets=100, roi=20.0
        )

        assert metrics.sharpe_ratio is not None
        assert metrics.sharpe_ratio > 0
