"""Tests for Telegram service and API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.telegram_service import TelegramService


@pytest.fixture
async def telegram_service(db_session: AsyncSession) -> TelegramService:
    """Create TelegramService instance for testing."""
    return TelegramService(db_session)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestTelegramService:
    """Test TelegramService methods."""

    @pytest.mark.asyncio
    async def test_generate_link_token(
        self, telegram_service: TelegramService, test_user: User
    ):
        """Test token generation."""
        with patch.object(telegram_service, "_get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client

            token = await telegram_service.generate_link_token(test_user.id)

            assert token is not None
            assert len(token) == 36  # UUID format
            mock_redis_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_link_token_valid(
        self, telegram_service: TelegramService, test_user: User
    ):
        """Test validating a valid token."""
        with patch.object(telegram_service, "_get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = str(test_user.id)
            mock_redis.return_value = mock_redis_client

            user_id = await telegram_service.validate_link_token("valid-token")

            assert user_id == test_user.id
            mock_redis_client.get.assert_called_once_with("telegram_link:valid-token")

    @pytest.mark.asyncio
    async def test_validate_link_token_invalid(
        self, telegram_service: TelegramService
    ):
        """Test validating an invalid token."""
        with patch.object(telegram_service, "_get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = None
            mock_redis.return_value = mock_redis_client

            user_id = await telegram_service.validate_link_token("invalid-token")

            assert user_id is None

    @pytest.mark.asyncio
    async def test_link_telegram_account(
        self, telegram_service: TelegramService, test_user: User, db_session: AsyncSession  # noqa: ARG002
    ):
        """Test linking a Telegram account."""
        with patch.object(telegram_service, "_get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = str(test_user.id)
            mock_redis.return_value = mock_redis_client

            # Generate token first
            token = await telegram_service.generate_link_token(test_user.id)

            # Link account
            linked_user = await telegram_service.link_telegram_account(
                token, "123456789", "testuser"
            )

            assert linked_user is not None
            assert linked_user.id == test_user.id
            assert linked_user.telegram_chat_id == "123456789"
            assert linked_user.telegram_verified is True
            mock_redis_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_link_telegram_account_invalid_token(
        self, telegram_service: TelegramService
    ):
        """Test linking with invalid token."""
        with patch.object(telegram_service, "_get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = None
            mock_redis.return_value = mock_redis_client

            linked_user = await telegram_service.link_telegram_account(
                "invalid-token", "123456789", "testuser"
            )

            assert linked_user is None

    @pytest.mark.asyncio
    async def test_unlink_telegram_account(
        self, telegram_service: TelegramService, test_user: User, db_session: AsyncSession
    ):
        """Test unlinking a Telegram account."""
        # First link the account
        test_user.telegram_chat_id = "123456789"
        test_user.telegram_verified = True
        await db_session.commit()

        # Unlink
        success = await telegram_service.unlink_telegram_account(test_user.id)

        assert success is True
        await db_session.refresh(test_user)
        assert test_user.telegram_chat_id is None
        assert test_user.telegram_verified is False

    @pytest.mark.asyncio
    async def test_unlink_telegram_account_not_found(
        self, telegram_service: TelegramService
    ):
        """Test unlinking non-existent user."""
        success = await telegram_service.unlink_telegram_account(99999)
        assert success is False

    def test_get_deep_link_url(self, telegram_service: TelegramService):
        """Test deep link URL generation."""
        token = "test-token-123"
        url = telegram_service.get_deep_link_url(token)

        assert "t.me" in url
        assert token in url
        assert url.startswith("https://")

    @pytest.mark.asyncio
    async def test_get_telegram_status_linked(
        self, telegram_service: TelegramService, test_user: User, db_session: AsyncSession
    ):
        """Test getting status for linked account."""
        test_user.telegram_chat_id = "123456789"
        test_user.telegram_verified = True
        await db_session.commit()

        status = await telegram_service.get_telegram_status(test_user.id)

        assert status["linked"] is True
        assert status["verified"] is True
        assert status["chat_id"] == "123456789"

    @pytest.mark.asyncio
    async def test_get_telegram_status_not_linked(
        self, telegram_service: TelegramService, test_user: User
    ):
        """Test getting status for non-linked account."""
        status = await telegram_service.get_telegram_status(test_user.id)

        assert status["linked"] is False
        assert status["verified"] is False


class TestTelegramAPIEndpoints:
    """Test Telegram API endpoints."""

    @pytest.mark.asyncio
    async def test_generate_link_endpoint(self, client, auth_headers):
        """Test POST /auth/telegram/generate-link endpoint."""
        response = await client.post(
            "/api/v1/auth/telegram/generate-link",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "deep_link_url" in data
        assert "expires_in_seconds" in data
        assert "t.me" in data["deep_link_url"]

    @pytest.mark.asyncio
    async def test_get_status_endpoint(self, client, auth_headers):
        """Test GET /auth/telegram/status endpoint."""
        response = await client.get(
            "/api/v1/auth/telegram/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "linked" in data
        assert "verified" in data

    @pytest.mark.asyncio
    async def test_unlink_endpoint(self, client, auth_headers, test_user, db_session):
        """Test DELETE /auth/telegram/unlink endpoint."""
        # First link the account
        test_user.telegram_chat_id = "123456789"
        test_user.telegram_verified = True
        await db_session.commit()

        response = await client.delete(
            "/api/v1/auth/telegram/unlink",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_generate_link_unauthorized(self, client):
        """Test generate link without authentication."""
        response = await client.post("/api/v1/auth/telegram/generate-link")
        assert response.status_code == 403
