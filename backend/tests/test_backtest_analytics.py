"""Tests for enhanced backtest analytics."""

from datetime import datetime, timedelta

import pytest

from app.models.filter import Filter
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.models.user import User
from app.schemas.backtest import BacktestRequest, BetType
from app.services.backtest import BacktestService


class TestBacktestAnalytics:
    """Test enhanced backtest analytics features."""

    @pytest.fixture
    async def setup_data(self, db_session):
        """Set up test data with multiple fixtures."""
        # Create user
        user = User(
            email="analytics@test.com",
            password_hash="hashed",
            is_active=True,
        )
        db_session.add(user)

        # Create league
        league = League(
            league_id=1,
            season_type=2024,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db_session.add(league)

        # Create teams
        team1 = Team(team_id=1, name="Team1", display_name="Team One")
        team2 = Team(team_id=2, name="Team2", display_name="Team Two")
        db_session.add_all([team1, team2])

        await db_session.commit()

        # Create filter
        filter_obj = Filter(
            user_id=user.id,
            name="Analytics Test Filter",
            description="Test",
            rules=[],
            is_active=True,
        )
        db_session.add(filter_obj)
        await db_session.commit()

        # Create fixtures with varied results over 3 months
        base_date = datetime(2024, 1, 1)
        fixtures = []

        # January - 5 wins, 2 losses
        for i in range(7):
            score = (3, 1) if i < 5 else (1, 2)
            fixtures.append(
                Fixture(
                    event_id=100 + i,
                    league_id=1,
                    season_type=2024,
                    match_date=base_date + timedelta(days=i * 4),
                    home_team_id=1,
                    away_team_id=2,
                    home_team_score=score[0],
                    away_team_score=score[1],
                    status_id=28,
                )
            )

        # February - 3 losses, 4 wins
        for i in range(7):
            score = (1, 2) if i < 3 else (2, 0)
            fixtures.append(
                Fixture(
                    event_id=200 + i,
                    league_id=1,
                    season_type=2024,
                    match_date=base_date + timedelta(days=30 + i * 4),
                    home_team_id=1,
                    away_team_id=2,
                    home_team_score=score[0],
                    away_team_score=score[1],
                    status_id=28,
                )
            )

        # March - 6 wins
        for i in range(6):
            fixtures.append(
                Fixture(
                    event_id=300 + i,
                    league_id=1,
                    season_type=2024,
                    match_date=base_date + timedelta(days=60 + i * 4),
                    home_team_id=1,
                    away_team_id=2,
                    home_team_score=3,
                    away_team_score=1,
                    status_id=28,
                )
            )

        db_session.add_all(fixtures)
        await db_session.commit()

        return {"user": user, "filter": filter_obj, "fixtures": fixtures}

    async def test_calculate_streaks_winning(self, db_session):
        """Test streak calculation with winning streak."""
        service = BacktestService(db_session)

        results = [
            {"outcome": "win", "profit": 1.0},
            {"outcome": "win", "profit": 1.0},
            {"outcome": "win", "profit": 1.0},
            {"outcome": "loss", "profit": -1.0},
            {"outcome": "win", "profit": 1.0},
            {"outcome": "win", "profit": 1.0},
        ]

        streaks = service.calculate_streaks(results)

        assert streaks.current_streak == 2  # Currently on 2-win streak
        assert streaks.longest_winning_streak == 3
        assert streaks.longest_losing_streak == 1

    async def test_calculate_streaks_losing(self, db_session):
        """Test streak calculation with losing streak."""
        service = BacktestService(db_session)

        results = [
            {"outcome": "win", "profit": 1.0},
            {"outcome": "loss", "profit": -1.0},
            {"outcome": "loss", "profit": -1.0},
            {"outcome": "loss", "profit": -1.0},
        ]

        streaks = service.calculate_streaks(results)

        assert streaks.current_streak == -3  # Currently on 3-loss streak
        assert streaks.longest_winning_streak == 1
        assert streaks.longest_losing_streak == 3

    async def test_calculate_streaks_with_pushes(self, db_session):
        """Test that pushes don't affect streaks."""
        service = BacktestService(db_session)

        results = [
            {"outcome": "win", "profit": 1.0},
            {"outcome": "win", "profit": 1.0},
            {"outcome": "push", "profit": 0.0},
            {"outcome": "win", "profit": 1.0},
        ]

        streaks = service.calculate_streaks(results)

        # Push shouldn't break the streak - continues through
        assert streaks.current_streak == 3  # 3 wins (push doesn't count)
        assert streaks.longest_winning_streak == 3

    async def test_calculate_monthly_breakdown(self, db_session, setup_data):
        """Test monthly performance breakdown."""
        service = BacktestService(db_session)
        fixtures = setup_data["fixtures"]

        # Create results matching fixtures
        results = []
        for fixture in fixtures:
            outcome = "win" if fixture.home_team_score > fixture.away_team_score else "loss"
            profit = 1.0 if outcome == "win" else -1.0
            results.append({
                "fixture_id": fixture.id,
                "outcome": outcome,
                "profit": profit,
                "stake": 1.0,
            })

        monthly = service.calculate_monthly_breakdown(results, fixtures)

        assert len(monthly) == 3  # 3 months
        assert monthly[0].month == "2024-01"
        assert monthly[0].wins == 5
        assert monthly[0].losses == 3  # 8 total matches, 5 wins = 3 losses
        assert monthly[0].profit == 2.0  # 5 wins - 3 losses

        assert monthly[1].month == "2024-02"
        assert monthly[1].wins == 4
        assert monthly[1].losses == 2  # 6 total matches, 4 wins = 2 losses

        assert monthly[2].month == "2024-03"
        assert monthly[2].wins == 6
        assert monthly[2].losses == 0

    async def test_calculate_drawdown(self, db_session):
        """Test drawdown calculation."""
        service = BacktestService(db_session)

        # Simulate: +3, +2, -1, -2, -1, +4
        # Balance: 3, 5, 4, 2, 1, 5
        # Peak: 3, 5, 5, 5, 5, 5
        # Drawdown: 0, 0, 1, 3, 4, 0
        results = [
            {"profit": 3.0},
            {"profit": 2.0},
            {"profit": -1.0},
            {"profit": -2.0},
            {"profit": -1.0},
            {"profit": 4.0},
        ]

        drawdown = service.calculate_drawdown(results)

        assert drawdown.peak_balance == 5.0
        assert drawdown.max_drawdown == 4.0
        assert drawdown.max_drawdown_pct == 80.0  # 4/5 * 100
        assert drawdown.current_drawdown == 0.0  # Back at peak

    async def test_calculate_drawdown_continuous_loss(self, db_session):
        """Test drawdown with continuous losses."""
        service = BacktestService(db_session)

        results = [
            {"profit": 5.0},
            {"profit": -1.0},
            {"profit": -1.0},
            {"profit": -1.0},
        ]

        drawdown = service.calculate_drawdown(results)

        assert drawdown.peak_balance == 5.0
        assert drawdown.max_drawdown == 3.0
        assert drawdown.current_drawdown == 3.0  # Still in drawdown

    async def test_generate_profit_curve(self, db_session, setup_data):
        """Test profit curve generation."""
        service = BacktestService(db_session)
        fixtures = setup_data["fixtures"][:10]  # Use first 10 fixtures

        results = []
        for i, fixture in enumerate(fixtures):
            profit = 1.0 if i % 2 == 0 else -1.0
            results.append({
                "fixture_id": fixture.id,
                "profit": profit,
            })

        curve = service.generate_profit_curve(results, fixtures)

        assert len(curve) == 10
        assert curve[0].match_number == 1
        assert curve[0].cumulative_profit == 1.0
        assert curve[1].match_number == 2
        assert curve[1].cumulative_profit == 0.0  # 1 - 1
        assert curve[2].cumulative_profit == 1.0  # 0 + 1
        assert all(point.date is not None for point in curve)

    async def test_generate_profit_curve_downsampling(self, db_session):
        """Test profit curve downsampling for large datasets."""
        service = BacktestService(db_session)

        # Create 2000 results
        results = [{"fixture_id": i, "profit": 0.5} for i in range(2000)]
        fixtures = []

        curve = service.generate_profit_curve(results, fixtures)

        # Should be downsampled to max 1000 points
        assert len(curve) <= 1000

    async def test_enhanced_backtest_with_analytics(self, db_session, setup_data):
        """Test full backtest with analytics enabled."""
        service = BacktestService(db_session)
        filter_obj = setup_data["filter"]

        request = BacktestRequest(
            bet_type=BetType.HOME_WIN,
            seasons=[2024],
            stake=1.0,
        )

        response = await service.run_backtest(
            filter_obj, request, include_analytics=True
        )

        # Check basic response
        assert response.total_matches > 0
        assert response.filter_id == filter_obj.id

        # Check analytics are included
        assert response.analytics is not None
        assert response.analytics.streaks is not None
        assert response.analytics.monthly_breakdown is not None
        assert response.analytics.drawdown is not None
        assert response.analytics.profit_curve is not None

        # Verify analytics data
        assert len(response.analytics.monthly_breakdown) > 0
        assert len(response.analytics.profit_curve) > 0

    async def test_backtest_without_analytics(self, db_session, setup_data):
        """Test backtest without analytics returns standard response."""
        service = BacktestService(db_session)
        filter_obj = setup_data["filter"]

        request = BacktestRequest(
            bet_type=BetType.HOME_WIN,
            seasons=[2024],
            stake=1.0,
        )

        response = await service.run_backtest(
            filter_obj, request, include_analytics=False
        )

        # Should be standard BacktestResponse without analytics
        assert not hasattr(response, "analytics") or response.analytics is None

    async def test_empty_results_analytics(self, db_session):
        """Test analytics with empty results."""
        service = BacktestService(db_session)

        streaks = service.calculate_streaks([])
        assert streaks.current_streak == 0
        assert streaks.longest_winning_streak == 0

        monthly = service.calculate_monthly_breakdown([], [])
        assert len(monthly) == 0

        drawdown = service.calculate_drawdown([])
        assert drawdown.max_drawdown == 0.0

        curve = service.generate_profit_curve([], [])
        assert len(curve) == 0
