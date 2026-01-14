"""Tests for teams endpoints."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.team import Team
from app.models.team_stats import TeamStats


class TestTeamsEndpoints:
    """Tests for teams API endpoints."""

    async def test_get_team_by_id(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting a single team by ID."""
        team = Team(
            team_id=1,
            name="Arsenal",
            display_name="Arsenal FC",
            abbreviation="ARS",
        )
        db_session.add(team)
        await db_session.flush()

        response = await client.get(f"/api/v1/teams/{team.team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == 1
        assert data["name"] == "Arsenal"
        assert data["display_name"] == "Arsenal FC"

    async def test_get_team_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent team."""
        response = await client.get("/api/v1/teams/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_team_match_stats(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting team statistics for a specific match."""
        from datetime import datetime

        from app.models.league import League

        # Create league first
        league = League(
            season_type=2,
            year=2023,
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

        # Create fixture
        fixture = Fixture(
            event_id=12345,
            season_type=2,
            league_id=39,
            match_date=datetime(2024, 1, 1),
            home_team_id=1,
            away_team_id=2,
            status_id=3,
        )
        db_session.add(fixture)
        await db_session.flush()

        # Create stats
        stats = TeamStats(
            season_type=2,
            event_id=12345,
            team_id=1,
            possession_pct=65.5,
            total_shots=15.0,
            shots_on_target=8.0,
        )
        db_session.add(stats)
        await db_session.flush()

        response = await client.get("/api/v1/teams/1/stats/12345")
        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == 1
        assert data["event_id"] == 12345
        assert data["possession_pct"] == 65.5
        assert data["total_shots"] == 15.0

    async def test_get_team_match_stats_not_found(
        self, client: AsyncClient
    ) -> None:
        """Test getting stats for non-existent match."""
        response = await client.get("/api/v1/teams/1/stats/99999")
        assert response.status_code == 404

    async def test_get_team_form_no_matches(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting team form when no matches exist."""
        team = Team(
            team_id=1,
            name="Arsenal",
            display_name="Arsenal FC",
        )
        db_session.add(team)
        await db_session.flush()

        response = await client.get("/api/v1/teams/1/form")
        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == 1
        assert data["team_name"] == "Arsenal FC"
        assert data["matches"] == []
        assert data["wins"] == 0
        assert data["draws"] == 0
        assert data["losses"] == 0

    async def test_get_team_form_with_matches(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting team form with match history."""
        from datetime import datetime, timedelta

        from app.models.league import League

        # Create league first
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
        team3 = Team(team_id=3, name="Liverpool", display_name="Liverpool FC")
        db_session.add_all([team1, team2, team3])
        await db_session.flush()

        # Create fixtures (Arsenal wins, draws, loses)
        base_date = datetime(2024, 1, 1)

        fixtures = [
            # Arsenal 3-1 Chelsea (Win)
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                home_team_score=3,
                away_team_score=1,
                home_team_winner=True,
                away_team_winner=False,
                status_id=3,
            ),
            # Liverpool 2-2 Arsenal (Draw)
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=7),
                home_team_id=3,
                away_team_id=1,
                home_team_score=2,
                away_team_score=2,
                home_team_winner=False,
                away_team_winner=False,
                status_id=3,
            ),
            # Arsenal 0-2 Chelsea (Loss)
            Fixture(
                event_id=3,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=14),
                home_team_id=1,
                away_team_id=2,
                home_team_score=0,
                away_team_score=2,
                home_team_winner=False,
                away_team_winner=True,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        response = await client.get("/api/v1/teams/1/form?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == 1
        assert len(data["matches"]) == 3
        assert data["wins"] == 1
        assert data["draws"] == 1
        assert data["losses"] == 1
        assert data["goals_for"] == 5  # 3 + 2 + 0
        assert data["goals_against"] == 5  # 1 + 2 + 2
        assert data["form_string"] == "LDW"  # Most recent first

    async def test_get_team_form_not_found(self, client: AsyncClient) -> None:
        """Test getting form for non-existent team."""
        response = await client.get("/api/v1/teams/99999/form")
        assert response.status_code == 404

    async def test_get_head_to_head_no_matches(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test head-to-head with no matches."""
        team1 = Team(team_id=1, name="Arsenal", display_name="Arsenal FC")
        team2 = Team(team_id=2, name="Chelsea", display_name="Chelsea FC")
        db_session.add_all([team1, team2])
        await db_session.flush()

        response = await client.get("/api/v1/teams/head-to-head/1/2")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_head_to_head_with_matches(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test head-to-head with match history."""
        from datetime import datetime, timedelta

        from app.models.league import League

        # Create league first
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

        base_date = datetime(2024, 1, 1)

        fixtures = [
            Fixture(
                event_id=1,
                season_type=2,
                league_id=39,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                home_team_score=3,
                away_team_score=1,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                season_type=2,
                league_id=39,
                match_date=base_date + timedelta(days=180),
                home_team_id=2,
                away_team_id=1,
                home_team_score=2,
                away_team_score=2,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.flush()

        response = await client.get("/api/v1/teams/head-to-head/1/2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Most recent first
        assert data[0]["event_id"] == 2
        assert data[1]["event_id"] == 1
