"""Tests for authentication endpoints."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import create_user


class TestRegistration:
    """Tests for user registration endpoint."""

    async def test_register_new_user(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 201
        data = response.json()
        # Response now includes tokens and user info
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert "id" in data["user"]
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    async def test_register_duplicate_email(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test registration with duplicate email fails."""
        # Create existing user
        await create_user(db_session, "existing@example.com", "password123")

        # Try to register with same email
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "existing@example.com", "password": "newpassword123"},
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "testpassword123"},
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient) -> None:
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login endpoint."""

    async def test_login_success(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test successful login returns tokens and user info."""
        # Create user
        await create_user(db_session, "user@example.com", "password123")

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "user@example.com"

    async def test_login_wrong_password(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test login with wrong password fails."""
        # Create user
        await create_user(db_session, "user@example.com", "password123")

        # Try to login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401

    async def test_login_inactive_user(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test login with inactive user fails."""
        # Create inactive user
        user = await create_user(db_session, "inactive@example.com", "password123")
        user.is_active = False
        await db_session.commit()

        # Try to login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    async def test_refresh_token_success(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test successful token refresh."""
        # Create user and login
        await create_user(db_session, "user@example.com", "password123")
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_with_access_token_fails(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test refresh with access token instead of refresh token fails."""
        # Create user and login
        await create_user(db_session, "user@example.com", "password123")
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        access_token = login_response.json()["access_token"]

        # Try to refresh with access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401

    async def test_refresh_with_invalid_token(self, client: AsyncClient) -> None:
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code == 401


class TestProtectedEndpoint:
    """Tests for protected endpoint access."""

    async def test_get_current_user_success(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test accessing protected endpoint with valid token."""
        # Create user and login
        await create_user(db_session, "user@example.com", "password123")
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        access_token = login_response.json()["access_token"]

        # Access protected endpoint
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@example.com"

    async def test_get_current_user_no_token(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint without token fails."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_get_current_user_invalid_token(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint with invalid token fails."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    async def test_get_current_user_with_refresh_token_fails(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test accessing protected endpoint with refresh token fails."""
        # Create user and login
        await create_user(db_session, "user@example.com", "password123")
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Try to access with refresh token
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401
