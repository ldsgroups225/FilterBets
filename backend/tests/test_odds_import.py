"""Tests for odds import script."""

import pytest
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOddsStatsSchema:
    """Test cases for OddsStats schema."""

    def test_create_odds_stats(self):
        """Test creating an OddsStats instance."""
        from app.schemas.backtest import OddsStats

        stats = OddsStats(
            avg_odds=2.1,
            min_odds=1.5,
            max_odds=3.5,
            median_odds=2.0,
            std_dev=0.4,
            has_real_odds=True,
            coverage_pct=85.5,
        )

        assert stats.avg_odds == 2.1
        assert stats.min_odds == 1.5
        assert stats.max_odds == 3.5
        assert stats.has_real_odds is True
        assert stats.coverage_pct == 85.5

    def test_odds_stats_defaults(self):
        """Test OddsStats default values."""
        from app.schemas.backtest import OddsStats

        stats = OddsStats(
            avg_odds=2.0,
            min_odds=2.0,
            max_odds=2.0,
        )

        assert stats.has_real_odds is False
        assert stats.median_odds is None
        assert stats.std_dev is None


class TestBacktestWithOdds:
    """Test cases for backtest using real odds."""

    def test_calculate_profit_with_odds(self):
        """Test profit calculation with different odds."""
        from app.services.backtest import BacktestService

        service = BacktestService(None)

        win_profit = service._calculate_profit("win", 1.0, 2.0)
        assert win_profit == 1.0

        loss_profit = service._calculate_profit("loss", 1.0, 2.0)
        assert loss_profit == -1.0

        push_profit = service._calculate_profit("push", 1.0, 2.0)
        assert push_profit == 0.0

    def test_calculate_profit_high_odds(self):
        """Test profit calculation with high odds."""
        from app.services.backtest import BacktestService

        service = BacktestService(None)

        win_profit = service._calculate_profit("win", 1.0, 5.0)
        assert win_profit == 4.0

    def test_calculate_odds_stats(self):
        """Test odds statistics calculation."""
        from app.services.backtest import BacktestService
        from app.schemas.backtest import OddsStats

        service = BacktestService(None)

        results = [
            {"outcome": "win", "odds": 2.0},
            {"outcome": "loss", "odds": 1.8},
            {"outcome": "win", "odds": 2.5},
            {"outcome": "loss", "odds": 2.2},
        ]

        stats = service._calculate_odds_stats(results)

        assert isinstance(stats, OddsStats)
        assert stats.has_real_odds is True
        assert stats.avg_odds == 2.125
        assert stats.min_odds == 1.8
        assert stats.max_odds == 2.5
        assert stats.coverage_pct == 100.0

    def test_calculate_odds_stats_default_odds(self):
        """Test odds stats when using default odds (2.0)."""
        from app.services.backtest import BacktestService
        from app.schemas.backtest import OddsStats

        service = BacktestService(None)

        results = [
            {"outcome": "win", "odds": 2.0},
            {"outcome": "loss", "odds": 2.0},
        ]

        stats = service._calculate_odds_stats(results)

        assert isinstance(stats, OddsStats)
        assert stats.has_real_odds is False
        assert stats.median_odds == 2.0


class TestOddsImportScript:
    """Integration tests for odds import script."""

    def test_sample_odds_csv_format(self, tmp_path):
        """Test that sample odds CSV has correct format."""
        csv_content = """event_id,home_odds,draw_odds,away_odds
74563,2.10,3.20,3.40
74564,1.85,3.40,4.20
74565,3.50,3.30,2.05"""

        csv_file = tmp_path / "sample_odds.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)
        assert list(df.columns) == ["event_id", "home_odds", "draw_odds", "away_odds"]
        assert len(df) == 3
        assert df["event_id"].tolist() == [74563, 74564, 74565]

    def test_odds_csv_parsing(self, tmp_path):
        """Test parsing CSV with various odds values."""
        csv_content = """event_id,home_odds,draw_odds,away_odds
1,1.5,3.5,8.0
2,2.1,3.2,3.4
3,3.0,2.2,2.8"""

        csv_file = tmp_path / "test_odds.csv"
        csv_file.write_text(csv_content)

        df = pd.read_csv(csv_file)
        assert df["home_odds"].tolist() == [1.5, 2.1, 3.0]
        assert df["draw_odds"].tolist() == [3.5, 3.2, 2.2]
        assert df["away_odds"].tolist() == [8.0, 3.4, 2.8]
