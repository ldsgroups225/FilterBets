"""Notification history API endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.filter import Filter
from app.models.filter_match import FilterMatch
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.models.user import User
from app.schemas.notification import NotificationHistoryItem, NotificationListResponse
from app.utils.pagination import paginate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notification_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """Get notification history for current user.

    Args:
        page: Page number
        per_page: Items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        NotificationListResponse with paginated notifications
    """
    # Build query for user's filter matches
    query = (
        select(FilterMatch)
        .join(Filter, FilterMatch.filter_id == Filter.id)
        .where(Filter.user_id == current_user.id)
        .order_by(FilterMatch.matched_at.desc())
    )

    # Paginate results
    filter_matches, meta = await paginate(db, query, page, per_page)

    # Build response items with related data
    items: list[NotificationHistoryItem] = []

    for filter_match in filter_matches:
        # Get filter
        filter_result = await db.execute(
            select(Filter).where(Filter.id == filter_match.filter_id)
        )
        filter_obj = filter_result.scalar_one_or_none()

        # Get fixture
        fixture_result = await db.execute(
            select(Fixture).where(Fixture.id == filter_match.fixture_id)
        )
        fixture = fixture_result.scalar_one_or_none()

        if not filter_obj or not fixture:
            continue

        # Get teams
        home_team_result = await db.execute(
            select(Team).where(Team.id == fixture.home_team_id)
        )
        home_team = home_team_result.scalar_one_or_none()

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
            continue

        items.append(
            NotificationHistoryItem(
                id=filter_match.id,
                filter_id=filter_match.filter_id,
                filter_name=filter_obj.name,
                fixture_id=filter_match.fixture_id,
                home_team=home_team.name,
                away_team=away_team.name,
                league_name=league.league_name,
                match_date=fixture.match_date,
                matched_at=filter_match.matched_at,
                notification_sent=filter_match.notification_sent,
                notification_sent_at=filter_match.notification_sent_at,
                notification_error=filter_match.notification_error,
                bet_result=filter_match.bet_result.value,
            )
        )

    return NotificationListResponse(items=items, meta=meta)
