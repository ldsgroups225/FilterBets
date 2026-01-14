"""Tests for fixtures endpoints."""

from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team


class TestFixturesEndpoints:
    """Tests for fixtures API endpoints."""

    async def test_get_fixtures_empty(self, client: AsyncClient) -> None:
        """Test getting fixtures when database is empty."""
        response = await client.get("/api/v1/fixtures")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert data["items"] == []
        assert data["meta"]["total_items"] == 0

    async def test_get_fixtures_with_data(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting fixtures with data."""
        # Create league
        league = League(
            season_type=2,
            year=2024,
            season_name="Test League",
            league_id=39,
            league_name="Test League",
        )
        db_session.add(league)
        await db_session.flush()

        # Create teams
        team1 = Team(team_id=1, name="Arsenal", display_name="Arsenal FC")
        team2 = Team(team_id=2, name="Chelsea", display_name="Chelsea FC")
        db_session.add_all([team1, team2])
        await db_session.flush()

        # Create fixtures
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                home_team_score=2,
                away_team_score=1,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=7),
                home_team_id=2,
                away_team_id=1,
                status_id=1,  # Not started
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        response = await client.get("/api/v1/fixtures")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["total_items"] == 2

    async def test_get_fixtures_filter_by_league(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test filtering fixtures by league."""
        # Create leagues
        league1 = League(
            season_type=2, year=2024, season_name="League 1", league_id=39, league_name="League 1"
        )
        league2 = League(
            season_type=2, year=2024, season_name="League 2", league_id=140, league_name="League 2"
        )
        db_session.add_all([league1, league2])
        await db_session.flush()

        # Create teams
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([team1, team2])
        await db_session.flush()

        # Create fixtures in different leagues
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=140,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        # Filter by league 39
        response = await client.get("/api/v1/fixtures?league_id=39")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["league_id"] == 39

    async def test_get_fixtures_filter_by_date(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test filtering fixtures by date range."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create fixtures across different dates
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=15),
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            ),
            Fixture(
                event_id=3,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=30),
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        # Filter by date range
        date_from = (base_date + timedelta(days=10)).isoformat()
        date_to = (base_date + timedelta(days=20)).isoformat()
        response = await client.get(
            f"/api/v1/fixtures?date_from={date_from}&date_to={date_to}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["event_id"] == 2

    async def test_get_fixtures_filter_by_status(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test filtering fixtures by status."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create fixtures with different statuses
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                status_id=3,  # Completed
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=1),
                home_team_id=1,
                away_team_id=2,
                status_id=1,  # Not started
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        # Filter by completed status
        response = await client.get("/api/v1/fixtures?status=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status_id"] == 3

    async def test_get_fixtures_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test fixtures pagination."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create 5 fixtures
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=i,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=i),
                home_team_id=1,
                away_team_id=2,
                status_id=3,
            )
            for i in range(1, 6)
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        # Test pagination
        response = await client.get("/api/v1/fixtures?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["total_items"] == 5
        assert data["meta"]["total_pages"] == 3
        assert data["meta"]["has_next"] is True

    async def test_get_today_fixtures_empty(self, client: AsyncClient) -> None:
        """Test getting today's fixtures when none exist."""
        response = await client.get("/api/v1/fixtures/today")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    async def test_get_today_fixtures(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting today's fixtures."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create fixtures - today and tomorrow
        today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=today,
                home_team_id=1,
                away_team_id=2,
                status_id=1,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=tomorrow,
                home_team_id=1,
                away_team_id=2,
                status_id=1,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        response = await client.get("/api/v1/fixtures/today")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["event_id"] == 1

    async def test_get_upcoming_fixtures(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting upcoming fixtures."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(team_id=1, name="Team1", display_name="Team 1")
        team2 = Team(team_id=2, name="Team2", display_name="Team 2")
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create fixtures in the future
        now = datetime.now()
        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=now + timedelta(days=2),
                home_team_id=1,
                away_team_id=2,
                status_id=1,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=now + timedelta(days=5),
                home_team_id=1,
                away_team_id=2,
                status_id=1,
            ),
            Fixture(
                event_id=3,
                season_type=2,
                league_id=39,
                match_date=now + timedelta(days=10),
                home_team_id=1,
                away_team_id=2,
                status_id=1,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        # Get upcoming fixtures for next 7 days
        response = await client.get("/api/v1/fixtures/upcoming?days=7")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2  # Only first 2 are within 7 days

    async def test_get_fixture_detail(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting detailed fixture information."""
        # Create league and teams
        league = League(
            season_type=2, year=2024, season_name="Test", league_id=39, league_name="Test"
        )
        team1 = Team(
            team_id=1,
            name="Arsenal",
            display_name="Arsenal FC",
            logo_url="https://example.com/arsenal.png",
        )
        team2 = Team(
            team_id=2,
            name="Chelsea",
            display_name="Chelsea FC",
            logo_url="https://example.com/chelsea.png",
        )
        db_session.add_all([league, team1, team2])
        await db_session.flush()

        # Create fixture
        fixture = Fixture(
            event_id=1,
            season_type=2,
            league_id=39,
            match_date=datetime(2024, 1, 1),
            home_team_id=1,
            away_team_id=2,
            home_team_score=3,
            away_team_score=1,
            home_team_winner=True,
            away_team_winner=False,
            status_id=3,
        )
        db_session.add(fixture)
        await db_session.flush()

        response = await client.get(f"/api/v1/fixtures/{fixture.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == 1
        assert data["home_team"]["team_id"] == 1
        assert data["home_team"]["display_name"] == "Arsenal FC"
        assert data["home_team"]["score"] == 3
        assert data["home_team"]["is_winner"] is True
        assert data["away_team"]["team_id"] == 2
        assert data["away_team"]["display_name"] == "Chelsea FC"
        assert data["away_team"]["score"] == 1
        assert data["away_team"]["is_winner"] is False

    async def test_get_fixture_detail_not_found(self, client: AsyncClient) -> None:
        """Test getting non-existent fixture."""
        response = await client.get("/api/v1/fixtures/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
