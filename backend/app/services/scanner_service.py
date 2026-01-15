"""Pre-match scanner service for automated filter matching."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.filter import Filter
from app.models.filter_match import FilterMatch
from app.models.fixture import Fixture
from app.models.user import User
from app.services.filter_engine import FilterEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class ScanStats:
    """Statistics from a scanner run."""

    def __init__(self) -> None:
        self.users_scanned: int = 0
        self.filters_evaluated: int = 0
        self.fixtures_checked: int = 0
        self.new_matches_found: int = 0
        self.notifications_queued: int = 0
        self.errors: int = 0
        self.scan_duration_seconds: float = 0.0


class PreMatchScanner:
    """Service for scanning upcoming fixtures against user filters."""

    def __init__(self, db: AsyncSession):
        """Initialize scanner service.

        Args:
            db: Async database session
        """
        self.db = db
        self.filter_engine = FilterEngine(db)

    async def get_upcoming_fixtures(
        self, lookahead_hours: int | None = None
    ) -> list[Fixture]:
        """Fetch upcoming fixtures within the lookahead window.

        Args:
            lookahead_hours: Hours to look ahead (default from settings)

        Returns:
            List of upcoming fixtures
        """
        if lookahead_hours is None:
            lookahead_hours = settings.scanner_lookahead_hours

        now = datetime.utcnow()
        end_time = now + timedelta(hours=lookahead_hours)

        # Query fixtures that are:
        # 1. In the future (match_date > now)
        # 2. Within lookahead window (match_date <= end_time)
        # 3. Not finished (status_id != 28)
        result = await self.db.execute(
            select(Fixture)
            .where(Fixture.match_date > now)
            .where(Fixture.match_date <= end_time)
            .where(Fixture.status_id != 28)  # 28 = Full Time
            .order_by(Fixture.match_date)
        )

        fixtures = list(result.scalars().all())
        logger.info(
            f"Found {len(fixtures)} upcoming fixtures in next {lookahead_hours} hours"
        )
        return fixtures

    async def get_users_with_active_alerts(self) -> list[User]:
        """Fetch users who have verified Telegram and active filter alerts.

        Returns:
            List of users with active alerts
        """
        # Subquery to check if user has at least one active filter with alerts enabled
        has_active_alerts = (
            select(Filter.id)
            .where(Filter.user_id == User.id)
            .where(Filter.is_active == True)  # noqa: E712
            .where(Filter.alerts_enabled == True)  # noqa: E712
            .limit(1)
            .exists()
        )

        result = await self.db.execute(
            select(User)
            .where(User.telegram_verified == True)  # noqa: E712
            .where(User.telegram_chat_id.isnot(None))
            .where(has_active_alerts)
        )

        users = list(result.scalars().all())
        logger.info(f"Found {len(users)} users with active alerts")
        return users

    async def scan_filters_for_user(
        self, user: User, fixtures: list[Fixture]
    ) -> list[tuple[Filter, list[Fixture]]]:
        """Apply user's filters to fixtures and return matches.

        Args:
            user: User to scan filters for
            fixtures: List of fixtures to check

        Returns:
            List of tuples (filter, matching_fixtures)
        """
        # Get user's active filters with alerts enabled
        result = await self.db.execute(
            select(Filter)
            .where(Filter.user_id == user.id)
            .where(Filter.is_active == True)  # noqa: E712
            .where(Filter.alerts_enabled == True)  # noqa: E712
        )
        filters = list(result.scalars().all())

        matches: list[tuple[Filter, list[Fixture]]] = []

        for filter_obj in filters:
            try:
                # Extract rules from filter
                rules = filter_obj.rules.get("conditions", [])
                if not rules:
                    logger.warning(f"Filter {filter_obj.id} has no conditions")
                    continue

                # Get fixture IDs to check
                fixture_ids = [f.id for f in fixtures]

                # Use filter engine to find matching fixtures
                # Note: We pass fixtures through filter engine by date range
                if fixtures:
                    min_date = min(f.match_date for f in fixtures).date()
                    max_date = max(f.match_date for f in fixtures).date()

                    matching_fixtures = await self.filter_engine.find_matching_fixtures(
                        rules=rules,
                        date_from=min_date,
                        date_to=max_date,
                        limit=len(fixtures),
                    )

                    # Filter to only fixtures in our list
                    matching_fixtures = [
                        f for f in matching_fixtures if f.id in fixture_ids
                    ]

                    if matching_fixtures:
                        matches.append((filter_obj, matching_fixtures))
                        logger.info(
                            f"Filter {filter_obj.id} matched {len(matching_fixtures)} fixtures"
                        )

            except Exception as e:
                logger.error(f"Error evaluating filter {filter_obj.id}: {e}")
                continue

        return matches

    async def get_new_matches(
        self, filter_id: int, fixture_ids: list[int]
    ) -> list[int]:
        """Filter out already-notified filter+fixture combinations.

        Args:
            filter_id: Filter ID
            fixture_ids: List of fixture IDs to check

        Returns:
            List of fixture IDs that haven't been notified yet
        """
        if not fixture_ids:
            return []

        # Query existing filter_matches
        result = await self.db.execute(
            select(FilterMatch.fixture_id)
            .where(FilterMatch.filter_id == filter_id)
            .where(FilterMatch.fixture_id.in_(fixture_ids))
        )
        existing_fixture_ids = set(result.scalars().all())

        # Return only new fixture IDs
        new_fixture_ids = [fid for fid in fixture_ids if fid not in existing_fixture_ids]

        logger.info(
            f"Filter {filter_id}: {len(new_fixture_ids)} new matches "
            f"out of {len(fixture_ids)} total"
        )
        return new_fixture_ids

    async def record_filter_match(
        self, filter_id: int, fixture_id: int
    ) -> FilterMatch | None:
        """Record a filter match in the database.

        Args:
            filter_id: Filter ID
            fixture_id: Fixture ID

        Returns:
            Created FilterMatch object or None if already exists
        """
        try:
            # Check if already exists (race condition protection)
            result = await self.db.execute(
                select(FilterMatch)
                .where(FilterMatch.filter_id == filter_id)
                .where(FilterMatch.fixture_id == fixture_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.debug(
                    f"FilterMatch already exists: filter={filter_id}, fixture={fixture_id}"
                )
                return None

            # Create new filter match
            filter_match = FilterMatch(
                filter_id=filter_id,
                fixture_id=fixture_id,
                matched_at=datetime.utcnow(),
                notification_sent=False,
            )

            self.db.add(filter_match)
            await self.db.commit()
            await self.db.refresh(filter_match)

            logger.info(f"Recorded filter match: {filter_match.id}")
            return filter_match

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error recording filter match: {e}")
            return None

    async def run_full_scan(self) -> ScanStats:
        """Run a full scan of all users and their filters.

        Returns:
            ScanStats object with scan results
        """
        start_time = datetime.utcnow()
        stats = ScanStats()

        try:
            logger.info("Starting pre-match scanner run")

            # Get upcoming fixtures
            fixtures = await self.get_upcoming_fixtures()
            stats.fixtures_checked = len(fixtures)

            if not fixtures:
                logger.info("No upcoming fixtures to scan")
                return stats

            # Get users with active alerts
            users = await self.get_users_with_active_alerts()
            stats.users_scanned = len(users)

            if not users:
                logger.info("No users with active alerts")
                return stats

            # Scan each user's filters
            for user in users:
                try:
                    matches = await self.scan_filters_for_user(user, fixtures)
                    stats.filters_evaluated += len(matches)

                    # Process matches
                    for filter_obj, matching_fixtures in matches:
                        fixture_ids = [f.id for f in matching_fixtures]

                        # Get only new matches (not already notified)
                        new_fixture_ids = await self.get_new_matches(
                            filter_obj.id, fixture_ids
                        )

                        # Record new matches
                        for fixture_id in new_fixture_ids:
                            filter_match = await self.record_filter_match(
                                filter_obj.id, fixture_id
                            )
                            if filter_match:
                                stats.new_matches_found += 1
                                stats.notifications_queued += 1

                                # Safety limit check
                                if (
                                    stats.notifications_queued
                                    >= settings.scanner_max_notifications_per_scan
                                ):
                                    logger.warning(
                                        f"Reached max notifications limit: "
                                        f"{settings.scanner_max_notifications_per_scan}"
                                    )
                                    break

                        if (
                            stats.notifications_queued
                            >= settings.scanner_max_notifications_per_scan
                        ):
                            break

                    if (
                        stats.notifications_queued
                        >= settings.scanner_max_notifications_per_scan
                    ):
                        break

                except Exception as e:
                    logger.error(f"Error scanning user {user.id}: {e}")
                    stats.errors += 1
                    continue

            # Calculate duration
            end_time = datetime.utcnow()
            stats.scan_duration_seconds = (end_time - start_time).total_seconds()

            logger.info(
                f"Scanner run complete: {stats.new_matches_found} new matches found, "
                f"{stats.notifications_queued} notifications queued in "
                f"{stats.scan_duration_seconds:.2f}s"
            )

        except Exception as e:
            logger.error(f"Fatal error in scanner run: {e}")
            stats.errors += 1

        return stats
