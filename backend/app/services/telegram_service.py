"""Telegram service for managing bot integration and deep linking."""

import logging
import uuid
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramService:
    """Service for Telegram bot operations and account linking."""

    def __init__(self, db: AsyncSession):
        """Initialize Telegram service.

        Args:
            db: Async database session
        """
        self.db = db
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        """Get or create Redis connection.

        Returns:
            Redis client instance
        """
        if self._redis is None:
            self._redis = await aioredis.from_url(
                settings.redis_url, encoding="utf-8", decode_responses=True
            )
        return self._redis

    async def generate_link_token(self, user_id: int) -> str:
        """Generate a unique token for Telegram account linking.

        Args:
            user_id: User ID to link

        Returns:
            UUID token string
        """
        token = str(uuid.uuid4())
        redis = await self._get_redis()

        # Store token in Redis with TTL (30 minutes)
        key = f"telegram_link:{token}"
        await redis.setex(key, settings.telegram_link_token_ttl, str(user_id))

        logger.info(f"Generated Telegram link token for user {user_id}")
        return token

    async def validate_link_token(self, token: str) -> int | None:
        """Validate a Telegram link token and return associated user ID.

        Args:
            token: Token to validate

        Returns:
            User ID if token is valid, None otherwise
        """
        redis = await self._get_redis()
        key = f"telegram_link:{token}"

        user_id_str = await redis.get(key)
        if user_id_str is None:
            logger.warning(f"Invalid or expired Telegram link token: {token}")
            return None

        return int(user_id_str)

    async def link_telegram_account(
        self, token: str, telegram_chat_id: str, telegram_username: str | None = None
    ) -> User | None:
        """Link a Telegram account to a user.

        Args:
            token: Link token from deep link
            telegram_chat_id: Telegram chat ID
            telegram_username: Optional Telegram username

        Returns:
            Updated User object if successful, None otherwise
        """
        # Validate token and get user ID
        user_id = await self.validate_link_token(token)
        if user_id is None:
            return None

        # Get user from database
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            logger.error(f"User {user_id} not found for Telegram linking")
            return None

        # Update user with Telegram info
        user.telegram_chat_id = telegram_chat_id
        user.telegram_verified = True
        await self.db.commit()
        await self.db.refresh(user)

        # Delete the used token
        redis = await self._get_redis()
        await redis.delete(f"telegram_link:{token}")

        logger.info(
            f"Successfully linked Telegram account {telegram_chat_id} to user {user_id}"
        )
        return user

    async def unlink_telegram_account(self, user_id: int) -> bool:
        """Unlink Telegram account from a user.

        Args:
            user_id: User ID to unlink

        Returns:
            True if successful, False otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            logger.error(f"User {user_id} not found for Telegram unlinking")
            return False

        user.telegram_chat_id = None
        user.telegram_verified = False
        await self.db.commit()

        logger.info(f"Successfully unlinked Telegram account from user {user_id}")
        return True

    def get_deep_link_url(self, token: str) -> str:
        """Generate Telegram deep link URL.

        Args:
            token: Link token

        Returns:
            Deep link URL string
        """
        return f"https://t.me/{settings.telegram_bot_username}?start={token}"

    async def get_telegram_status(self, user_id: int) -> dict[str, Any]:
        """Get Telegram link status for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with link status information
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            return {"linked": False, "verified": False}

        return {
            "linked": user.telegram_chat_id is not None,
            "verified": user.telegram_verified,
            "chat_id": user.telegram_chat_id,
        }

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis is not None:
            await self._redis.close()
