"""Tests for backtest service and endpoints."""

from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter import Filter
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.schemas.backtest import BacktestRequest, BetType
from app.services.backtest import BacktestService


class TestBacktestService:
    """Tests for BacktestService."""

    @pytest.fixture
    async def league(self, db: AsyncSession) -> League:
        """Create a test league."""
        league = League(
            league_id=100,
            league_name="Test League",
            season_name="2024 Season",
            season_type=2024,
            year=2024,
        )
        db.add(league)
        await db.commit()
        await db.refresh(league)
        return league

    @pytest.fixture
    async def teams(self, db: AsyncSession) -> tuple[Team, Team]:
        """Create test teams."""
        home_team = Team(
            team_id=1001,
            name="Home FC",
            display_name="Home FC",
        )
        away_team = Team(
            team_id=1002,
            name="Away United",
            display_name="Away United",
        )
        db.add_all([home_team, away_team])
        await db.commit()
        await db.refresh(home_team)
        await db.refresh(away_team)
        return home_team, away_team

    @pytest.fixture
    async def fixtures_data(
        self, db: AsyncSession, league: League, teams: tuple[Team, Team]
    ) -> list[Fixture]:
        """Create test fixtures with various outcomes."""
        home_team, away_team = teams
        fixtures = [
            # Home win (3-1)
            Fixture(
                event_id=5001,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 1, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=3,
                away_team_score=1,
                home_team_winner=True,
                away_team_winner=False,
                status_id=28,  # Full Time
            ),
            # Away win (0-2)
            Fixture(
                event_id=5002,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 2, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=0,
                away_team_score=2,
                home_team_winner=False,
                away_team_winner=True,
                status_id=28,
            ),
            # Draw (1-1)
            Fixture(
                event_id=5003,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 3, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=1,
                away_team_score=1,
                home_team_winner=False,
                away_team_winner=False,
                status_id=28,
            ),
            # High scoring (3-2, over 2.5)
            Fixture(
                event_id=5004,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 4, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=3,
                away_team_score=2,
                home_team_winner=True,
                away_team_winner=False,
                status_id=28,
            ),
            # Low scoring (0-0, under 2.5)
            Fixture(
                event_id=5005,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 5, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=0,
                away_team_score=0,
                home_team_winner=False,
                away_team_winner=False,
                status_id=28,
            ),
        ]
        db.add_all(fixtures)
        await db.commit()
        for f in fixtures:
            await db.refresh(f)
        return fixtures

    @pytest.fixture
    async def test_filter(self, db: AsyncSession, test_user, league: League) -> Filter:
        """Create a test filter."""
        filter_obj = Filter(
            user_id=test_user.id,
            name="Test Backtest Filter",
            rules=[{"field": "league_id", "operator": "=", "value": league.league_id}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.commit()
        await db.refresh(filter_obj)
        return filter_obj

    async def test_backtest_home_win(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test backtest for home_win bet type."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        assert result.filter_id == test_filter.id
        assert result.bet_type == "home_win"
        assert result.total_matches == 5
        assert result.wins == 2  # 3-1 and 3-2
        assert result.losses == 3  # 0-2, 1-1, 0-0
        assert result.cached is False

    async def test_backtest_away_win(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test backtest for away_win bet type."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.AWAY_WIN, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        assert result.wins == 1  # 0-2
        assert result.losses == 4

    async def test_backtest_draw(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test backtest for draw bet type."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.DRAW, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        assert result.wins == 2  # 1-1 and 0-0
        assert result.losses == 3

    async def test_backtest_over_2_5(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test backtest for over_2_5 bet type."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.OVER_2_5, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        assert result.wins == 2  # 3-1 (4 goals) and 3-2 (5 goals)
        assert result.losses == 3  # 0-2, 1-1, 0-0

    async def test_backtest_under_2_5(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test backtest for under_2_5 bet type."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.UNDER_2_5, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        assert result.wins == 3  # 0-2, 1-1, 0-0
        assert result.losses == 2  # 3-1, 3-2

    async def test_backtest_caching(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test that backtest results are cached."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024])

        # First run - not cached
        result1 = await service.run_backtest(test_filter, request)
        assert result1.cached is False

        # Second run - should be cached
        result2 = await service.run_backtest(test_filter, request)
        assert result2.cached is True
        assert result2.wins == result1.wins
        assert result2.losses == result1.losses

    async def test_backtest_cache_invalidation(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test cache invalidation."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024])

        # Run backtest to create cache
        await service.run_backtest(test_filter, request)

        # Invalidate cache
        await service.invalidate_cache(test_filter.id)

        # Next run should not be cached
        result = await service.run_backtest(test_filter, request)
        assert result.cached is False

    async def test_backtest_win_rate_calculation(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test win rate calculation."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024])

        result = await service.run_backtest(test_filter, request)

        # 2 wins out of 5 = 40%
        assert result.win_rate == 40.0

    async def test_backtest_roi_calculation(
        self, db: AsyncSession, test_filter: Filter, fixtures_data: list[Fixture]  # noqa: ARG002
    ):
        """Test ROI calculation."""
        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024], stake=1.0)

        result = await service.run_backtest(test_filter, request)

        # 2 wins * 1.0 profit - 3 losses * 1.0 = -1.0 total profit
        # ROI = -1.0 / 5.0 * 100 = -20%
        assert result.total_profit == -1.0
        assert result.roi_percentage == -20.0

    async def test_backtest_no_matches(self, db: AsyncSession, test_user):
        """Test backtest with no matching fixtures."""
        # Create filter for non-existent league
        filter_obj = Filter(
            user_id=test_user.id,
            name="Empty Filter",
            rules=[{"field": "league_id", "operator": "=", "value": 99999}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.commit()
        await db.refresh(filter_obj)

        service = BacktestService(db)
        request = BacktestRequest(bet_type=BetType.HOME_WIN, seasons=[2024])

        result = await service.run_backtest(filter_obj, request)

        assert result.total_matches == 0
        assert result.wins == 0
        assert result.losses == 0
        assert result.win_rate == 0.0
        assert result.roi_percentage == 0.0


class TestBacktestEndpoint:
    """Tests for backtest API endpoint."""

    @pytest.fixture
    async def league(self, db: AsyncSession) -> League:
        """Create a test league."""
        league = League(
            league_id=200,
            league_name="API Test League",
            season_name="2024 Season",
            season_type=2024,
            year=2024,
        )
        db.add(league)
        await db.commit()
        await db.refresh(league)
        return league

    @pytest.fixture
    async def teams(self, db: AsyncSession) -> tuple[Team, Team]:
        """Create test teams."""
        home_team = Team(
            team_id=2001,
            name="API Home FC",
            display_name="API Home FC",
        )
        away_team = Team(
            team_id=2002,
            name="API Away United",
            display_name="API Away United",
        )
        db.add_all([home_team, away_team])
        await db.commit()
        return home_team, away_team

    @pytest.fixture
    async def fixtures_data(
        self, db: AsyncSession, league: League, teams: tuple[Team, Team]
    ) -> list[Fixture]:
        """Create test fixtures."""
        home_team, away_team = teams
        fixtures = [
            Fixture(
                event_id=6001,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 1, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=2,
                away_team_score=0,
                home_team_winner=True,
                away_team_winner=False,
                status_id=28,
            ),
            Fixture(
                event_id=6002,
                season_type=2024,
                league_id=league.league_id,
                match_date=datetime(2024, 2, 15),
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                home_team_score=1,
                away_team_score=1,
                home_team_winner=False,
                away_team_winner=False,
                status_id=28,
            ),
        ]
        db.add_all(fixtures)
        await db.commit()
        return fixtures

    async def test_backtest_endpoint_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db: AsyncSession,
        test_user,
        league: League,
        fixtures_data: list[Fixture],  # noqa: ARG002
    ):
        """Test successful backtest via API."""
        # Create filter
        filter_obj = Filter(
            user_id=test_user.id,
            name="API Test Filter",
            rules=[{"field": "league_id", "operator": "=", "value": league.league_id}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.commit()
        await db.refresh(filter_obj)

        response = await client.post(
            f"/api/v1/filters/{filter_obj.id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filter_id"] == filter_obj.id
        assert data["bet_type"] == "home_win"
        assert data["total_matches"] == 2
        assert data["wins"] == 1
        assert data["losses"] == 1

    async def test_backtest_endpoint_unauthorized(self, client: AsyncClient):
        """Test backtest without authentication."""
        response = await client.post(
            "/api/v1/filters/1/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
        )

        # FastAPI returns 403 for missing credentials with OAuth2
        assert response.status_code in [401, 403]

    async def test_backtest_endpoint_filter_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test backtest with non-existent filter."""
        response = await client.post(
            "/api/v1/filters/99999/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_backtest_endpoint_not_owner(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_user,
        league: League,
    ):
        """Test backtest on filter owned by another user."""
        from app.models.user import User
        from app.utils.security import create_access_token, get_password_hash

        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password123"),
            is_active=True,
        )
        db.add(other_user)
        await db.commit()
        await db.refresh(other_user)

        # Create filter owned by other user
        filter_obj = Filter(
            user_id=other_user.id,
            name="Other User Filter",
            rules=[{"field": "league_id", "operator": "=", "value": league.league_id}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.commit()
        await db.refresh(filter_obj)

        # Try to backtest with test_user's token
        token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/filters/{filter_obj.id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers=headers,
        )

        assert response.status_code == 404

    async def test_backtest_endpoint_invalid_bet_type(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db: AsyncSession,
        test_user,
        league: League,
    ):
        """Test backtest with invalid bet type."""
        filter_obj = Filter(
            user_id=test_user.id,
            name="Test Filter",
            rules=[{"field": "league_id", "operator": "=", "value": league.league_id}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.commit()
        await db.refresh(filter_obj)

        response = await client.post(
            f"/api/v1/filters/{filter_obj.id}/backtest",
            json={"bet_type": "invalid_type", "seasons": [2024]},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error
