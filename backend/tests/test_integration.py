"""Integration tests for FilterBets system.

Tests cover:
- Filter-to-outcome correlation
- Backtest determinism
- Authentication flows
- MCP endpoint access
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import create_user


class TestFilterToOutcomeCorrelation:
    """Tests for filter rules correlating with match outcomes."""

    async def test_high_scoring_filter_correlates_with_over_2_5(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that filters targeting high-scoring teams correlate with over 2.5 goals."""
        user = await create_user(db_session, "test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/",
            json={
                "name": "High Scoring Teams",
                "description": "Filter for high-scoring teams",
                "rules": [
                    {"field": "home_form_goals_scored_5", "operator": ">", "value": 1.5}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert response.status_code == 201
        filter_id = response.json()["id"]

        backtest_response = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "over_2_5", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert backtest_response.status_code == 200
        data = backtest_response.json()

        assert "win_rate" in data
        assert "roi_percentage" in data
        assert "total_matches" in data

    async def test_home_form_filter_correlates_with_home_wins(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that filters for good home form correlate with home wins."""
        user = await create_user(db_session, "test2@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/",
            json={
                "name": "Strong Home Teams",
                "description": "Filter for strong home teams",
                "rules": [
                    {"field": "home_form_wins_5", "operator": ">=", "value": 3}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert response.status_code == 201
        filter_id = response.json()["id"]

        backtest_response = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert backtest_response.status_code == 200
        data = backtest_response.json()

        assert data["win_rate"] >= 40

    async def test_filter_with_no_matches_returns_empty_results(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that restrictive filters return zero matches."""
        user = await create_user(db_session, "test3@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/",
            json={
                "name": "Impossible Filter",
                "description": "Filter that should match nothing",
                "rules": [
                    {"field": "home_form_goals_scored_5", "operator": ">", "value": 100}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert response.status_code == 201
        filter_id = response.json()["id"]

        backtest_response = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert backtest_response.status_code == 200
        data = backtest_response.json()

        assert data["total_matches"] == 0


class TestBacktestDeterminism:
    """Tests for backtest result consistency."""

    async def test_same_filter_same_result(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that running the same backtest twice returns same results."""
        user = await create_user(db_session, "test4@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/",
            json={
                "name": "Determinism Test Filter",
                "description": "Test filter for determinism",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 1}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert response.status_code == 201
        filter_id = response.json()["id"]

        backtest1 = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "over_2_5", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        backtest2 = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "over_2_5", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        assert backtest1.status_code == 200
        assert backtest2.status_code == 200

        result1 = backtest1.json()
        result2 = backtest2.json()

        assert result1["win_rate"] == result2["win_rate"]
        assert result1["total_matches"] == result2["total_matches"]
        assert result1["total_profit"] == result2["total_profit"]

    async def test_cached_result_returned_on_repeated_request(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that cached results are returned on repeated requests."""
        user = await create_user(db_session, "test5@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/",
            json={
                "name": "Cache Test Filter",
                "description": "Test filter for caching",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 2}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )
        assert response.status_code == 201
        filter_id = response.json()["id"]

        await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        second_response = await client.post(
            f"/api/v1/filters/{filter_id}/backtest",
            json={"bet_type": "home_win", "seasons": [2024]},
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        assert second_response.status_code == 200
        data = second_response.json()
        assert "cached" in data


class TestAuthenticationFlows:
    """Tests for authentication and authorization."""

    async def test_login_returns_valid_token(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that login returns a valid JWT token."""
        await create_user(db_session, "auth_test@example.com", "password123")

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "auth_test@example.com", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 50

    async def test_protected_endpoint_requires_auth(
        self, client: AsyncClient
    ) -> None:
        """Test that protected endpoints return 401 without auth."""
        response = await client.get("/api/v1/filters/")
        assert response.status_code == 401

    async def test_invalid_token_rejected(
        self, client: AsyncClient
    ) -> None:
        """Test that invalid tokens are rejected."""
        response = await client.get(
            "/api/v1/filters/",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401

    async def test_expired_token_rejected(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that expired tokens are rejected."""
        await create_user(db_session, "expired_test@example.com", "password123")

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "expired_test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        response = await client.get(
            "/api/v1/filters/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestMCPAccess:
    """Tests for MCP endpoint access."""

    async def test_mcp_requires_auth(self, client: AsyncClient) -> None:
        """Test that MCP endpoint requires authentication."""
        response = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1},
            headers={"Accept": "text/event-stream"},
        )
        assert response.status_code == 401

    async def test_mcp_with_valid_token(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that MCP endpoint accepts valid tokens."""
        user = await create_user(db_session, "mcp_test@example.com", "password123")

        response = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1},
            headers={
                "Authorization": f"Bearer {user.access_token}",
                "Accept": "text/event-stream",
            },
        )
        assert response.status_code == 200


class TestFilterValidation:
    """Tests for filter validation endpoint."""

    async def test_validate_filter_returns_match_count(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that validate endpoint returns estimated matches."""
        user = await create_user(db_session, "validate_test@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Test Filter",
                "rules": [
                    {"field": "league_id", "operator": "=", "value": 1}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "estimated_matches" in data
        assert "is_valid" in data

    async def test_validate_filter_rejects_post_match_fields(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that validation rejects post-match fields."""
        user = await create_user(db_session, "validate_test2@example.com", "password123")

        response = await client.post(
            "/api/v1/filters/validate",
            json={
                "name": "Invalid Filter",
                "rules": [
                    {"field": "home_team_score", "operator": ">", "value": 2}
                ],
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {user.access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0
