"""Tests for leagues endpoints."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.league import League


class TestLeaguesEndpoints:
    """Tests for leagues API endpoints."""

    async def test_get_leagues_empty(self, client: AsyncClient) -> None:
        """Test getting leagues when database is empty."""
        response = await client.get("/api/v1/leagues")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert data["items"] == []
        assert data["meta"]["total_items"] == 0

    async def test_get_leagues_with_data(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting leagues with data."""
        # Create test leagues
        league1 = League(
            season_type=2,
            year=2023,
            season_name="English Premier League 2023",
            league_id=39,
            league_name="English Premier League",
            league_short_name="Premier League",
        )
        league2 = League(
            season_type=2,
            year=2023,
            season_name="La Liga 2023",
            league_id=140,
            league_name="La Liga",
            league_short_name="La Liga",
        )
        db_session.add_all([league1, league2])
        await db_session.flush()

        response = await client.get("/api/v1/leagues")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["total_items"] == 2
        assert data["meta"]["total_pages"] == 1

    async def test_get_leagues_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test leagues pagination."""
        # Create 5 test leagues (reduced from 25 for faster tests)
        leagues = [
            League(
                season_type=2,
                year=2023,
                season_name=f"League {i}",
                league_id=100 + i,  # Unique league_id
                league_name=f"League {i}",
            )
            for i in range(5)
        ]
        db_session.add_all(leagues)
        await db_session.flush()

        # Test first page
        response = await client.get("/api/v1/leagues?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["total_items"] == 5
        assert data["meta"]["total_pages"] == 3
        assert data["meta"]["has_next"] is True
        assert data["meta"]["has_prev"] is False

        # Test second page
        response = await client.get("/api/v1/leagues?page=2&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["page"] == 2
        assert data["meta"]["has_next"] is True
        assert data["meta"]["has_prev"] is True

    async def test_get_league_by_id(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting a single league by ID."""
        league = League(
            season_type=2,
            year=2023,
            season_name="English Premier League 2023",
            league_id=39,
            league_name="English Premier League",
            league_short_name="Premier League",
        )
        db_session.add(league)
        await db_session.flush()

        response = await client.get(f"/api/v1/leagues/{league.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == league.id
        assert data["league_name"] == "English Premier League"
        assert data["league_id"] == 39

    async def test_get_league_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent league."""
        response = await client.get("/api/v1/leagues/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_league_teams(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test getting teams in a league."""
        league = League(
            season_type=2,
            year=2023,
            season_name="English Premier League 2023",
            league_id=39,
            league_name="English Premier League",
        )
        db_session.add(league)
        await db_session.flush()

        response = await client.get(f"/api/v1/leagues/{league.id}/teams")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data

    async def test_get_league_teams_not_found(self, client: AsyncClient) -> None:
        """Test getting teams for non-existent league."""
        response = await client.get("/api/v1/leagues/99999/teams")
        assert response.status_code == 404
