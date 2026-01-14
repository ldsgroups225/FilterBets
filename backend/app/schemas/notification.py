"""Pydantic schemas for notification endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import PaginationMeta


class NotificationHistoryItem(BaseModel):
    """Single notification history item."""

    id: int = Field(..., description="FilterMatch ID")
    filter_id: int = Field(..., description="Filter ID")
    filter_name: str = Field(..., description="Filter name")
    fixture_id: int = Field(..., description="Fixture ID")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    league_name: str = Field(..., description="League name")
    match_date: datetime = Field(..., description="Match date and time")
    matched_at: datetime = Field(..., description="When filter matched")
    notification_sent: bool = Field(..., description="Whether notification was sent")
    notification_sent_at: datetime | None = Field(
        None, description="When notification was sent"
    )
    notification_error: str | None = Field(None, description="Error message if failed")
    bet_result: str = Field(..., description="Bet outcome (pending/win/loss/push)")

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated list of notifications."""

    items: list[NotificationHistoryItem] = Field(..., description="Notification items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    model_config = {"from_attributes": True}
