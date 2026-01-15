"""Pydantic schemas for Telegram endpoints."""

from pydantic import BaseModel, Field


class TelegramLinkResponse(BaseModel):
    """Response for generating Telegram link."""

    deep_link_url: str = Field(..., description="Telegram deep link URL")
    expires_in_seconds: int = Field(..., description="Token expiry time in seconds")

    model_config = {"from_attributes": True}


class TelegramStatusResponse(BaseModel):
    """Response for Telegram link status."""

    linked: bool = Field(..., description="Whether Telegram is linked")
    verified: bool = Field(..., description="Whether Telegram is verified")
    chat_id: str | None = Field(None, description="Telegram chat ID (if linked)")

    model_config = {"from_attributes": True}


class TelegramUnlinkResponse(BaseModel):
    """Response for unlinking Telegram."""

    success: bool = Field(..., description="Whether unlink was successful")
    message: str = Field(..., description="Status message")

    model_config = {"from_attributes": True}
