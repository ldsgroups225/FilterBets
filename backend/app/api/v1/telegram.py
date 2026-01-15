"""Telegram API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import get_settings
from app.models.user import User
from app.schemas.telegram import (
    TelegramLinkResponse,
    TelegramStatusResponse,
    TelegramUnlinkResponse,
)
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/generate-link", response_model=TelegramLinkResponse)
async def generate_telegram_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TelegramLinkResponse:
    """Generate a Telegram deep link for account linking.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        TelegramLinkResponse with deep link URL
    """
    telegram_service = TelegramService(db)

    try:
        # Generate link token
        token = await telegram_service.generate_link_token(current_user.id)

        # Get deep link URL
        deep_link_url = telegram_service.get_deep_link_url(token)

        return TelegramLinkResponse(
            deep_link_url=deep_link_url,
            expires_in_seconds=settings.telegram_link_token_ttl,
        )

    finally:
        await telegram_service.close()


@router.get("/status", response_model=TelegramStatusResponse)
async def get_telegram_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TelegramStatusResponse:
    """Get Telegram link status for current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        TelegramStatusResponse with link status
    """
    telegram_service = TelegramService(db)

    try:
        status = await telegram_service.get_telegram_status(current_user.id)
        return TelegramStatusResponse(**status)

    finally:
        await telegram_service.close()


@router.delete("/unlink", response_model=TelegramUnlinkResponse)
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TelegramUnlinkResponse:
    """Unlink Telegram account from current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        TelegramUnlinkResponse with success status
    """
    telegram_service = TelegramService(db)

    try:
        success = await telegram_service.unlink_telegram_account(current_user.id)

        if success:
            return TelegramUnlinkResponse(
                success=True,
                message="Telegram account unlinked successfully",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to unlink Telegram account",
            )

    finally:
        await telegram_service.close()
