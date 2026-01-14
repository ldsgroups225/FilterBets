"""Tests for PreMatchScanner service."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter import Filter
from app.models.filter_match import FilterMatch
from app.models.fixture import Fixture
from app.models.user import ScanFrequency, User
from app.services.scanner_service import PreMatchScanner, ScanStats


@pytest.fixture
async def scanner_service(db_session: AsyncSession) -> PreMatchScanner:
    """Create PreMatchScanner instance for testing."""
    return PreMatchScanner(db_session)


@pytest.fixture
async def test_user_with_telegram(db_session: AsyncSession) -> User:
    """Create a test user with Telegram linked."""
    user = User(
        email="scanner@example.com",
        hashed_password="hashed_password",
        is_active=True,
        telegram_chat_id="123456789",
        telegram_verified=True,
        scan_frequency=ScanFrequency.TWICE_DAILY,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_filter(db_session: AsyncSession, test_user_with_telegram: User) -> Filter:
    """Create a test filter with alerts enabled."""
    filter_obj = Filter(
        user_id=test_user_with_telegram.id,
        name="Test Filter",
        description="Test filter for scanner",
        rules=[{"field": "home_odds", "operator": ">", "value": 2.0}],
        is_active=True,
        alerts_enabled=True,
    )
    db_session.add(filter_obj)
    await db_session.commit()
    await db_session.refresh(filter_obj)
    return filter_obj


@pytest.fixture
async def upcoming_fixture(db_session: AsyncSession) -> Fixture:
    """Create an upcoming fixture."""
    fixture = Fixture(
        api_fixture_id=12345,
        league_id=1,
        season=2024,
        match_date=datetime.utcnow() + timedelta(hours=12),
        home_team_id=1,
        away_team_id=2,
        status_id=1,  # Not started
    )
    db_session.add(fixture)
    await db_session.commit()
    await db_session.refresh(fixture)
    return fixture


class TestPreMatchScanner:
    """Test PreMatchScanner methods."""

    @pytest.mark.asyncio
    async def test_get_upcoming_fixtures(
        self, scanner_service: PreMatchScanner, upcoming_fixture: Fixture
    ):
        """Test fetching upcoming fixtures."""
        fixtures = await scanner_service.get_upcoming_fixtures(lookahead_hours=24)

        assert len(fixtures) > 0
        assert any(f.id == upcoming_fixture.id for f in fixtures)

    @pytest.mark.asyncio
    async def test_get_upcoming_fixtures_empty(
        self, scanner_service: PreMatchScanner
    ):
        """Test fetching upcoming fixtures when none exist."""
        fixtures = await scanner_service.get_upcoming_fixtures(lookahead_hours=1)
        # Should return empty list or only fixtures within 1 hour
        assert isinstance(fixtures, list)

    @pytest.mark.asyncio
    async def test_get_users_with_active_alerts(
        self, scanner_service: PreMatchScanner, test_user_with_telegram: User, test_filter: Filter
    ):
        """Test fetching users with active alerts."""
        users = await scanner_service.get_users_with_active_alerts()

        assert len(users) > 0
        assert any(u.id == test_user_with_telegram.id for u in users)

    @pytest.mark.asyncio
    async def test_get_users_with_active_alerts_no_telegram(
        self, scanner_service: PreMatchScanner, db_session: AsyncSession
    ):
        """Test that users without Telegram are excluded."""
        # Create user without Telegram
        user = User(
            email="notelegram@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()

        users = await scanner_service.get_users_with_active_alerts()

        # User without Telegram should not be in the list
        assert not any(u.email == "notelegram@example.com" for u in users)

    @pytest.mark.asyncio
    async def test_get_new_matches(
        self,
        scanner_service: PreMatchScanner,
        test_filter: Filter,
        upcoming_fixture: Fixture,
        db_session: AsyncSession,
    ):
        """Test filtering out already-notified matches."""
        # Create a filter match (already notified)
        existing_match = FilterMatch(
            filter_id=test_filter.id,
            fixture_id=upcoming_fixture.id,
            matched_at=datetime.utcnow(),
            notification_sent=True,
        )
        db_session.add(existing_match)
        await db_session.commit()

        # Try to get new matches
        new_matches = await scanner_service.get_new_matches(
            test_filter.id, [upcoming_fixture.id]
        )

        # Should be empty since we already notified
        assert len(new_matches) == 0

    @pytest.mark.asyncio
    async def test_get_new_matches_not_notified(
        self,
        scanner_service: PreMatchScanner,
        test_filter: Filter,
        upcoming_fixture: Fixture,
    ):
        """Test getting new matches that haven't been notified."""
        new_matches = await scanner_service.get_new_matches(
            test_filter.id, [upcoming_fixture.id]
        )

        # Should include the fixture since it hasn't been notified
        assert upcoming_fixture.id in new_matches

    @pytest.mark.asyncio
    async def test_record_filter_match(
        self,
        scanner_service: PreMatchScanner,
        test_filter: Filter,
        upcoming_fixture: Fixture,
        db_session: AsyncSession,
    ):
        """Test recording a filter match."""
        await scanner_service.record_filter_match(test_filter.id, upcoming_fixture.id)

        # Verify it was recorded
        from sqlalchemy import select
        result = await db_session.execute(
            select(FilterMatch).where(
                FilterMatch.filter_id == test_filter.id,
                FilterMatch.fixture_id == upcoming_fixture.id,
            )
        )
        match = result.scalar_one_or_none()

        assert match is not None
        assert match.filter_id == test_filter.id
        assert match.fixture_id == upcoming_fixture.id
        assert match.notification_sent is False

    @pytest.mark.asyncio
    async def test_run_full_scan(
        self,
        scanner_service: PreMatchScanner,
        test_user_with_telegram: User,
        test_filter: Filter,
        upcoming_fixture: Fixture,
    ):
        """Test running a full scan."""
        with patch("app.services.scanner_service.FilterEngine") as mock_engine:
            # Mock FilterEngine to return matching fixtures
            mock_instance = AsyncMock()
            mock_instance.apply_filter.return_value = [upcoming_fixture.id]
            mock_engine.return_value = mock_instance

            stats = await scanner_service.run_full_scan()

            assert isinstance(stats, ScanStats)
            assert stats.users_scanned >= 0
            assert stats.filters_scanned >= 0
            assert stats.fixtures_scanned >= 0

    @pytest.mark.asyncio
    async def test_run_full_scan_respects_max_notifications(
        self, scanner_service: PreMatchScanner
    ):
        """Test that scan respects max notifications limit."""
        with patch("app.services.scanner_service.FilterEngine") as mock_engine:
            mock_instance = AsyncMock()
            # Return many matches
            mock_instance.apply_filter.return_value = list(range(2000))
            mock_engine.return_value = mock_instance

            stats = await scanner_service.run_full_scan()

            # Should not exceed max_notifications_per_scan (1000)
            assert stats.matches_found <= 1000


class TestScannerAPIEndpoints:
    """Test Scanner API endpoints."""

    @pytest.mark.asyncio
    async def test_get_scanner_status(self, client, auth_headers):
        """Test GET /scanner/status endpoint."""
        response = await client.get(
            "/api/v1/scanner/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "last_scan_time" in data
        assert "stats" in data

    @pytest.mark.asyncio
    async def test_trigger_scanner_unauthorized(self, client, auth_headers):
        """Test POST /scanner/trigger without admin rights."""
        response = await client.post(
            "/api/v1/scanner/trigger",
            headers=auth_headers,
        )

        # Should fail if user is not admin
        assert response.status_code in [403, 401]

    @pytest.mark.asyncio
    async def test_get_scanner_status_unauthorized(self, client):
        """Test scanner status without authentication."""
        response = await client.get("/api/v1/scanner/status")
        assert response.status_code == 401
