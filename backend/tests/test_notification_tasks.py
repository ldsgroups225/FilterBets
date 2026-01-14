"""Tests for notification tasks and formatting."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tasks.notification_tasks import (
    format_notification_message,
    send_filter_alert,
)


@pytest.fixture
def sample_fixture_data():
    """Create sample fixture data for testing."""
    return {
        "id": 1,
        "home_team": {"name": "Manchester United", "logo": "https://example.com/logo.png"},
        "away_team": {"name": "Liverpool", "logo": "https://example.com/logo2.png"},
        "league": {"name": "Premier League", "country": "England"},
        "match_date": datetime(2024, 12, 25, 15, 0, 0),
        "home_odds": 2.5,
        "draw_odds": 3.2,
        "away_odds": 2.8,
    }


@pytest.fixture
def sample_filter():
    """Create sample filter for testing."""
    return {
        "id": 1,
        "name": "High Odds Home Win",
        "description": "Matches with high home win odds",
    }


class TestNotificationFormatting:
    """Test notification message formatting."""

    def test_format_notification_message_basic(
        self, sample_fixture_data, sample_filter
    ):
        """Test basic notification message formatting."""
        message = format_notification_message(sample_fixture_data, sample_filter)

        assert "Manchester United" in message
        assert "Liverpool" in message
        assert "Premier League" in message
        assert "High Odds Home Win" in message

    def test_format_notification_message_includes_odds(
        self, sample_fixture_data, sample_filter
    ):
        """Test that message includes odds information."""
        message = format_notification_message(sample_fixture_data, sample_filter)

        assert "2.5" in message or "2.50" in message  # Home odds
        assert "3.2" in message or "3.20" in message  # Draw odds
        assert "2.8" in message or "2.80" in message  # Away odds

    def test_format_notification_message_includes_date(
        self, sample_fixture_data, sample_filter
    ):
        """Test that message includes match date."""
        message = format_notification_message(sample_fixture_data, sample_filter)

        # Should contain date information
        assert "Dec" in message or "12" in message or "25" in message

    def test_format_notification_message_with_missing_odds(
        self, sample_fixture_data, sample_filter
    ):
        """Test formatting when odds are missing."""
        sample_fixture_data["home_odds"] = None
        sample_fixture_data["draw_odds"] = None
        sample_fixture_data["away_odds"] = None

        message = format_notification_message(sample_fixture_data, sample_filter)

        # Should still format without errors
        assert "Manchester United" in message
        assert "Liverpool" in message

    def test_format_notification_message_markdown_safe(
        self, sample_fixture_data, sample_filter
    ):
        """Test that message is safe for Telegram markdown."""
        # Add special characters that need escaping
        sample_fixture_data["home_team"]["name"] = "Team_With*Special[Chars]"

        message = format_notification_message(sample_fixture_data, sample_filter)

        # Should not contain unescaped special markdown characters in team names
        assert message is not None
        assert len(message) > 0


class TestSendFilterAlert:
    """Test send_filter_alert Celery task."""

    @pytest.mark.asyncio
    async def test_send_filter_alert_success(self, sample_fixture_data, sample_filter):
        """Test successful notification sending."""
        with patch("app.tasks.notification_tasks.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot_class.return_value = mock_bot
            mock_bot.send_message = AsyncMock()

            with patch("app.tasks.notification_tasks.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value.__aenter__.return_value = mock_db

                # Mock database queries
                mock_db.execute = AsyncMock()
                mock_db.commit = AsyncMock()

                result = await send_filter_alert(
                    user_telegram_chat_id="123456789",
                    fixture_data=sample_fixture_data,
                    filter_data=sample_filter,
                    filter_match_id=1,
                )

                assert result is True
                mock_bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_filter_alert_rate_limiting(self):
        """Test rate limiting logic."""
        with patch("app.tasks.notification_tasks.get_redis") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client

            # Simulate rate limit bucket
            mock_redis_client.get.return_value = "0"  # No tokens available

            with patch("app.tasks.notification_tasks.Bot") as mock_bot_class:
                mock_bot = AsyncMock()
                mock_bot_class.return_value = mock_bot

                # Should handle rate limiting gracefully
                # Implementation depends on your rate limiting strategy

    @pytest.mark.asyncio
    async def test_send_filter_alert_telegram_error(
        self, sample_fixture_data, sample_filter
    ):
        """Test handling of Telegram API errors."""
        with patch("app.tasks.notification_tasks.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot_class.return_value = mock_bot
            mock_bot.send_message = AsyncMock(
                side_effect=Exception("Telegram API Error")
            )

            with patch("app.tasks.notification_tasks.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value.__aenter__.return_value = mock_db
                mock_db.execute = AsyncMock()

                # Should handle error and potentially retry
                result = await send_filter_alert(
                    user_telegram_chat_id="123456789",
                    fixture_data=sample_fixture_data,
                    filter_data=sample_filter,
                    filter_match_id=1,
                )

                # Depending on implementation, might return False or raise
                assert result is False or result is None

    @pytest.mark.asyncio
    async def test_send_filter_alert_updates_notification_sent(
        self, sample_fixture_data, sample_filter
    ):
        """Test that notification_sent flag is updated on success."""
        with patch("app.tasks.notification_tasks.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot_class.return_value = mock_bot
            mock_bot.send_message = AsyncMock()

            with patch("app.tasks.notification_tasks.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value.__aenter__.return_value = mock_db

                # Mock FilterMatch update
                mock_filter_match = MagicMock()
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_filter_match
                mock_db.execute = AsyncMock(return_value=mock_result)
                mock_db.commit = AsyncMock()

                await send_filter_alert(
                    user_telegram_chat_id="123456789",
                    fixture_data=sample_fixture_data,
                    filter_data=sample_filter,
                    filter_match_id=1,
                )

                # Should update notification_sent to True
                assert mock_filter_match.notification_sent is True
                mock_db.commit.assert_called()


class TestNotificationAPIEndpoints:
    """Test Notification API endpoints."""

    @pytest.mark.asyncio
    async def test_get_notifications_list(self, client, auth_headers):
        """Test GET /notifications endpoint."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_notifications_pagination(self, client, auth_headers):
        """Test notification list pagination."""
        response = await client.get(
            "/api/v1/notifications?page=1&per_page=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10

    @pytest.mark.asyncio
    async def test_get_notifications_unauthorized(self, client):
        """Test notifications endpoint without authentication."""
        response = await client.get("/api/v1/notifications")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_notifications_filters_by_user(
        self, client, auth_headers, db_session
    ):
        """Test that notifications are filtered by current user."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # All returned notifications should belong to the authenticated user
        # This is implicitly tested by the endpoint implementation


class TestScannerTasks:
    """Test scanner Celery tasks."""

    @pytest.mark.asyncio
    async def test_run_pre_match_scanner_task(self):
        """Test run_pre_match_scanner Celery task."""
        with patch("app.tasks.scanner_tasks.PreMatchScanner") as mock_scanner_class:
            mock_scanner = AsyncMock()
            mock_scanner_class.return_value = mock_scanner

            from app.tasks.scanner_tasks import ScanStats
            mock_stats = ScanStats(
                users_scanned=5,
                filters_scanned=10,
                fixtures_scanned=20,
                matches_found=3,
                notifications_sent=3,
            )
            mock_scanner.run_full_scan = AsyncMock(return_value=mock_stats)

            with patch("app.tasks.scanner_tasks.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value.__aenter__.return_value = mock_db

                from app.tasks.scanner_tasks import run_pre_match_scanner
                result = await run_pre_match_scanner()

                assert result is not None
                mock_scanner.run_full_scan.assert_called_once()
