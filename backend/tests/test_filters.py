"""Tests for filter endpoints."""

from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter import Filter
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.models.user import User
from app.utils.security import create_access_token, get_password_hash


@pytest.fixture
async def test_user_for_filters(db: AsyncSession) -> User:
    """Create a test user for filter tests."""
    user = User(
        email="filtertest@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
async def filter_auth_headers(test_user_for_filters: User) -> dict[str, str]:
    """Get authentication headers for filter tests."""
    access_token = create_access_token({"sub": test_user_for_filters.email, "user_id": test_user_for_filters.id})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
class TestFilterCRUD:
    """Test filter CRUD operations."""

    async def test_create_filter_success(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test creating a new filter."""
        filter_data = {
            "name": "High Scoring Matches",
            "description": "Matches with more than 2 goals",
            "rules": [
                {"field": "home_score", "operator": ">", "value": 1},
                {"field": "status_id", "operator": "=", "value": 28},
            ],
            "is_active": True,
        }

        response = await client.post(
            "/api/v1/filters", json=filter_data, headers=filter_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == filter_data["name"]
        assert data["description"] == filter_data["description"]
        assert len(data["rules"]) == 2
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_create_filter_unauthorized(self, client: AsyncClient):
        """Test creating filter without authentication."""
        filter_data = {
            "name": "Test Filter",
            "rules": [{"field": "home_score", "operator": ">", "value": 2}],
        }

        response = await client.post("/api/v1/filters", json=filter_data)
        assert response.status_code == 403

    async def test_create_filter_invalid_field(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test creating filter with invalid field name."""
        filter_data = {
            "name": "Invalid Filter",
            "rules": [{"field": "invalid_field", "operator": "=", "value": 1}],
        }

        response = await client.post(
            "/api/v1/filters", json=filter_data, headers=filter_auth_headers
        )
        assert response.status_code == 422

    async def test_create_filter_too_many_conditions(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test creating filter with more than 10 conditions."""
        filter_data = {
            "name": "Too Many Conditions",
            "rules": [
                {"field": "home_score", "operator": ">", "value": i} for i in range(11)
            ],
        }

        response = await client.post(
            "/api/v1/filters", json=filter_data, headers=filter_auth_headers
        )
        assert response.status_code == 422

    async def test_create_filter_invalid_operator_value(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test creating filter with invalid value for 'in' operator."""
        filter_data = {
            "name": "Invalid In Operator",
            "rules": [
                {"field": "league_id", "operator": "in", "value": 1}
            ],  # Should be list
        }

        response = await client.post(
            "/api/v1/filters", json=filter_data, headers=filter_auth_headers
        )
        assert response.status_code == 422

    async def test_list_filters_empty(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test listing filters when user has none."""
        response = await client.get("/api/v1/filters", headers=filter_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total_items"] == 0

    async def test_list_filters_with_data(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test listing filters with data."""
        # Create filters
        filter1 = Filter(
            user_id=test_user_for_filters.id,
            name="Filter 1",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
            is_active=True,
        )
        filter2 = Filter(
            user_id=test_user_for_filters.id,
            name="Filter 2",
            rules=[{"field": "away_score", "operator": "<", "value": 1}],
            is_active=False,
        )
        db.add_all([filter1, filter2])
        await db.flush()

        response = await client.get("/api/v1/filters", headers=filter_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["total_items"] == 2
        assert len(data["items"]) == 2

    async def test_list_filters_filter_by_active(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test filtering filters by is_active status."""
        # Create filters
        filter1 = Filter(
            user_id=test_user_for_filters.id,
            name="Active Filter",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
            is_active=True,
        )
        filter2 = Filter(
            user_id=test_user_for_filters.id,
            name="Inactive Filter",
            rules=[{"field": "away_score", "operator": "<", "value": 1}],
            is_active=False,
        )
        db.add_all([filter1, filter2])
        await db.flush()

        response = await client.get(
            "/api/v1/filters?is_active=true", headers=filter_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["total_items"] == 1
        assert data["items"][0]["name"] == "Active Filter"

    async def test_get_filter_by_id(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test getting a specific filter."""
        filter_obj = Filter(
            user_id=test_user_for_filters.id,
            name="Test Filter",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        response = await client.get(
            f"/api/v1/filters/{filter_obj.id}", headers=filter_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == filter_obj.id
        assert data["name"] == "Test Filter"

    async def test_get_filter_not_found(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test getting non-existent filter."""
        response = await client.get(
            "/api/v1/filters/99999", headers=filter_auth_headers
        )
        assert response.status_code == 404

    async def test_get_filter_not_owner(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
    ):
        """Test getting filter owned by another user."""
        # Create another user and their filter
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            is_active=True,
        )
        db.add(other_user)
        await db.flush()
        await db.refresh(other_user)

        filter_obj = Filter(
            user_id=other_user.id,
            name="Other User Filter",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        response = await client.get(
            f"/api/v1/filters/{filter_obj.id}", headers=filter_auth_headers
        )
        assert response.status_code == 404

    async def test_update_filter(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test updating a filter."""
        filter_obj = Filter(
            user_id=test_user_for_filters.id,
            name="Original Name",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
            is_active=True,
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        update_data = {
            "name": "Updated Name",
            "is_active": False,
        }

        response = await client.put(
            f"/api/v1/filters/{filter_obj.id}",
            json=update_data,
            headers=filter_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_active"] is False

    async def test_update_filter_not_found(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test updating non-existent filter."""
        update_data = {"name": "Updated"}
        response = await client.put(
            "/api/v1/filters/99999", json=update_data, headers=filter_auth_headers
        )
        assert response.status_code == 404

    async def test_delete_filter(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test deleting a filter."""
        filter_obj = Filter(
            user_id=test_user_for_filters.id,
            name="To Delete",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        response = await client.delete(
            f"/api/v1/filters/{filter_obj.id}", headers=filter_auth_headers
        )
        assert response.status_code == 204

        # Verify deletion
        response = await client.get(
            f"/api/v1/filters/{filter_obj.id}", headers=filter_auth_headers
        )
        assert response.status_code == 404

    async def test_delete_filter_not_found(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test deleting non-existent filter."""
        response = await client.delete(
            "/api/v1/filters/99999", headers=filter_auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestFilterMatching:
    """Test filter matching functionality."""

    async def test_get_filter_matches_empty(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test getting matches when no fixtures match."""
        filter_obj = Filter(
            user_id=test_user_for_filters.id,
            name="No Matches",
            rules=[{"field": "home_score", "operator": ">", "value": 100}],
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        response = await client.get(
            f"/api/v1/filters/{filter_obj.id}/matches", headers=filter_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_filter_matches_with_data(
        self,
        client: AsyncClient,
        filter_auth_headers: dict[str, str],
        db: AsyncSession,
        test_user_for_filters: User,
    ):
        """Test getting matches with matching fixtures."""
        # Create league
        league = League(
            league_id=1,
            season_type=1,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db.add(league)
        await db.flush()

        # Create teams
        teams = [
            Team(team_id=i, name=f"Team {i}", display_name=f"Team {i}")
            for i in range(1, 5)
        ]
        db.add_all(teams)
        await db.flush()

        # Create fixtures
        fixture1 = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=28,
            home_team_id=1,
            away_team_id=2,
            home_team_score=3,
            away_team_score=1,
        )
        fixture2 = Fixture(
            id=2,
            league_id=1,
            event_id=1002,
            season_type=1,
            match_date=datetime(2024, 1, 16),
            status_id=28,
            home_team_id=3,
            away_team_id=4,
            home_team_score=1,
            away_team_score=0,
        )
        db.add_all([fixture1, fixture2])
        await db.flush()

        # Create filter for high home scores
        filter_obj = Filter(
            user_id=test_user_for_filters.id,
            name="High Home Scores",
            rules=[{"field": "home_score", "operator": ">", "value": 2}],
        )
        db.add(filter_obj)
        await db.flush()
        await db.refresh(filter_obj)

        response = await client.get(
            f"/api/v1/filters/{filter_obj.id}/matches", headers=filter_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1

    async def test_get_filter_matches_not_found(
        self, client: AsyncClient, filter_auth_headers: dict[str, str]
    ):
        """Test getting matches for non-existent filter."""
        response = await client.get(
            "/api/v1/filters/99999/matches", headers=filter_auth_headers
        )
        assert response.status_code == 404
