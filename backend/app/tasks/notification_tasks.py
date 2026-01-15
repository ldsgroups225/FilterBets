"""Celery tasks for sending Telegram notifications."""

import asyncio
import logging
import time
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from telegram import Bot
from telegram.error import TelegramError

from app.config import get_settings
from app.models.filter import Filter
from app.models.filter_match import FilterMatch
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async database session factory for tasks
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


class RateLimiter:
    """Token bucket rate limiter for Telegram API."""

    def __init__(self, redis_url: str, max_tokens: int = 30, refill_rate: float = 30.0):
        """Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
            max_tokens: Maximum tokens in bucket (messages per second)
            refill_rate: Tokens added per second
        """
        self.redis_url = redis_url
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.bucket_key = "telegram:rate_limit:bucket"
        self.last_refill_key = "telegram:rate_limit:last_refill"

    async def acquire(self) -> bool:
        """Acquire a token from the bucket.

        Returns:
            True if token acquired, False if rate limited
        """
        redis = await aioredis.from_url(
            self.redis_url, encoding="utf-8", decode_responses=True
        )

        try:
            now = time.time()

            # Get current bucket state
            tokens_str = await redis.get(self.bucket_key)
            last_refill_str = await redis.get(self.last_refill_key)

            tokens = float(tokens_str) if tokens_str else self.max_tokens
            last_refill = float(last_refill_str) if last_refill_str else now

            # Refill tokens based on time elapsed
            time_elapsed = now - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            tokens = min(self.max_tokens, tokens + tokens_to_add)

            # Try to consume a token
            if tokens >= 1.0:
                tokens -= 1.0
                await redis.set(self.bucket_key, str(tokens))
                await redis.set(self.last_refill_key, str(now))
                return True
            else:
                # Rate limited - wait time until next token
                wait_time = (1.0 - tokens) / self.refill_rate
                logger.warning(f"Rate limited. Wait {wait_time:.2f}s for next token")
                return False

        finally:
            await redis.close()


def format_notification_message(
    filter_name: str,
    home_team: str,
    away_team: str,
    league_name: str,
    match_date: str,
    match_url: str,
    stats: dict[str, Any] | None = None,
) -> str:
    """Format match data into Telegram notification message.

    Args:
        filter_name: Name of the filter that matched
        home_team: Home team name
        away_team: Away team name
        league_name: League name
        match_date: Match date/time string
        match_url: URL to match details
        stats: Optional dictionary of match statistics

    Returns:
        Formatted message string
    """
    message_lines = [
        "🎯 *FilterBets Alert*\n",
        f"Your filter *\"{filter_name}\"* matched:\n",
        f"⚽ *{home_team} vs {away_team}*",
        f"🏆 {league_name}",
        f"📅 {match_date}\n",
    ]

    # Add stats if provided
    if stats:
        message_lines.append("📊 *Key Stats:*")
        for key, value in stats.items():
            message_lines.append(f"• {key}: {value}")
        message_lines.append("")

    message_lines.append(f"🔗 [View Match Details]({match_url})")

    return "\n".join(message_lines)


@celery_app.task(
    name="app.tasks.notification_tasks.send_filter_alert",
    bind=True,
    autoretry_for=(TelegramError, ConnectionError),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def send_filter_alert(self: Any, filter_match_id: int) -> dict[str, Any]:
    """Send a Telegram notification for a filter match.

    Args:
        self: Celery task instance
        filter_match_id: FilterMatch ID to send notification for

    Returns:
        Dictionary with send status
    """
    return asyncio.run(_send_filter_alert_async(self, filter_match_id))


async def _send_filter_alert_async(
    _task: Any, filter_match_id: int
) -> dict[str, Any]:
    """Async implementation of send_filter_alert.

    Args:
        _task: Celery task instance (unused but required)
        filter_match_id: ID of the filter match to send alert for

    Args:
        task: Celery task instance
        filter_match_id: FilterMatch ID

    Returns:
        Dictionary with send status
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get filter match with related data
            result = await db.execute(
                select(FilterMatch)
                .where(FilterMatch.id == filter_match_id)
            )
            filter_match = result.scalar_one_or_none()

            if not filter_match:
                logger.error(f"FilterMatch {filter_match_id} not found")
                return {"status": "error", "message": "FilterMatch not found"}

            # Check if already sent
            if filter_match.notification_sent:
                logger.info(f"Notification already sent for FilterMatch {filter_match_id}")
                return {"status": "skipped", "message": "Already sent"}

            # Get related filter
            filter_result = await db.execute(
                select(Filter).where(Filter.id == filter_match.filter_id)
            )
            filter_obj = filter_result.scalar_one_or_none()

            if not filter_obj or not filter_obj.user.telegram_chat_id:
                logger.error(f"Filter {filter_match.filter_id} or user Telegram not found")
                return {"status": "error", "message": "Filter or Telegram not configured"}

            # Get fixture with teams and league
            fixture_result = await db.execute(
                select(Fixture)
                .where(Fixture.id == filter_match.fixture_id)
            )
            fixture = fixture_result.scalar_one_or_none()

            if not fixture:
                logger.error(f"Fixture {filter_match.fixture_id} not found")
                return {"status": "error", "message": "Fixture not found"}

            # Get home team
            home_team_result = await db.execute(
                select(Team).where(Team.id == fixture.home_team_id)
            )
            home_team = home_team_result.scalar_one_or_none()

            # Get away team
            away_team_result = await db.execute(
                select(Team).where(Team.id == fixture.away_team_id)
            )
            away_team = away_team_result.scalar_one_or_none()

            # Get league
            league_result = await db.execute(
                select(League).where(League.id == fixture.league_id)
            )
            league = league_result.scalar_one_or_none()

            if not home_team or not away_team or not league:
                logger.error("Missing team or league data")
                return {"status": "error", "message": "Missing related data"}

            # Rate limiting
            rate_limiter = RateLimiter(settings.redis_url)
            max_attempts = 5
            for attempt in range(max_attempts):
                if await rate_limiter.acquire():
                    break
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)  # Wait 1 second between attempts
                else:
                    logger.error("Rate limit exceeded after max attempts")
                    raise Exception("Rate limit exceeded")

            # Format message
            match_url = f"https://filterbets.com/fixtures/{fixture.id}"
            message = format_notification_message(
                filter_name=filter_obj.name,
                home_team=home_team.name,
                away_team=away_team.name,
                league_name=league.name,
                match_date=fixture.match_date.strftime("%b %d, %Y at %H:%M UTC"),
                match_url=match_url,
            )

            # Send via Telegram
            bot = Bot(token=settings.telegram_bot_token)
            await bot.send_message(
                chat_id=filter_obj.user.telegram_chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=False,
            )

            # Update filter_match as sent
            filter_match.notification_sent = True
            filter_match.notification_sent_at = asyncio.get_event_loop().time()
            await db.commit()

            logger.info(
                f"Sent notification for FilterMatch {filter_match_id} to "
                f"user {filter_obj.user_id}"
            )

            return {
                "status": "success",
                "filter_match_id": filter_match_id,
                "user_id": filter_obj.user_id,
            }

        except TelegramError as e:
            logger.error(f"Telegram error sending notification: {e}")
            # Update error in filter_match
            if filter_match:
                filter_match.notification_error = str(e)[:500]
                await db.commit()
            raise  # Let Celery retry

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            # Update error in filter_match
            if filter_match:
                filter_match.notification_error = str(e)[:500]
                await db.commit()
            return {"status": "error", "message": str(e)}
