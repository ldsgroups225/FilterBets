"""Tests for filter validation endpoint."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import create_user


class TestFilterValidation:
    """Tests for filter validation endpoint."""

    async def test_validate_valid_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation of a valid filter."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "description": "A test filter",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 1}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert len(data["errors"]) == 0
        assert data["estimated_matches"] >= 0

    async def test_validate_filter_missing_field(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation detects missing field."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "", "operator": "=", "value": 1}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("Missing field" in error for error in data["errors"])

    async def test_validate_filter_missing_operator(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation detects missing operator."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "", "value": 1}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("Missing operator" in error for error in data["errors"])

    async def test_validate_filter_missing_value(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation detects missing value."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": None}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("Missing value" in error for error in data["errors"])

    async def test_validate_filter_between_operator(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation of between operator requires list."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "home_team_score", "operator": "between", "value": "not-a-list"}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("between" in error.lower() for error in data["errors"])

    async def test_validate_filter_in_operator(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation of in operator requires list."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "in", "value": "not-a-list"}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("in" in error.lower() for error in data["errors"])

    async def test_validate_filter_with_post_match_field(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation rejects post-match fields."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "home_team_score", "operator": ">", "value": 2}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("post-match" in error.lower() or "post_match" in error.lower() for error in data["errors"])

    async def test_validate_filter_returns_match_count(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation returns estimated matches."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 1}
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "estimated_matches" in data
        assert "match_percentage" in data
        assert "seasons_available" in data

    async def test_validate_filter_too_many_rules(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test validation warns about too many rules."""
        await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 1},
                    {"field": "status_id", "operator": "=", "value": 28},
                    {"field": "home_team_id", "operator": "=", "value": 1},
                    {"field": "away_team_id", "operator": "=", "value": 2},
                    {"field": "league_id", "operator": "=", "value": 3},
                    {"field": "status_id", "operator": "=", "value": 4},
                    {"field": "home_team_id", "operator": "=", "value": 5},
                    {"field": "away_team_id", "operator": "=", "value": 6},
                    {"field": "league_id", "operator": "=", "value": 7},
                    {"field": "status_id", "operator": "=", "value": 8},
                    {"field": "home_team_id", "operator": "=", "value": 9},
                ],
                "is_active": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert any("10 rules" in warning for warning in data["warnings"])
