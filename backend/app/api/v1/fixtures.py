"""Fixtures API endpoints."""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.fixture import Fixture
from app.models.team import Team
from app.schemas.common import PaginatedResponse
from app.schemas.fixture import FixtureDetailResponse, FixtureResponse, TeamInFixture
from app.utils.pagination import paginate

router = APIRouter(prefix="/fixtures", tags=["fixtures"])


@router.get("", response_model=PaginatedResponse[FixtureResponse])
async def get_fixtures(
    db: Annotated[AsyncSession, Depends(get_db)],
    league_id: Annotated[int | None, Query(description="Filter by league ID")] = None,
    date_from: Annotated[
        datetime | None, Query(description="Filter fixtures from this date")
    ] = None,
    date_to: Annotated[
        datetime | None, Query(description="Filter fixtures until this date")
    ] = None,
    status: Annotated[
        int | None, Query(description="Filter by status ID (3=completed)")
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[FixtureResponse]:
    """Get paginated list of fixtures with optional filters.

    Args:
        db: Database session
        league_id: Optional league ID filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        status: Optional status ID filter
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Returns:
        Paginated list of fixtures
    """
    # Build query with filters
    query = select(Fixture)

    filters = []
    if league_id is not None:
        filters.append(Fixture.league_id == league_id)
    if date_from is not None:
        filters.append(Fixture.match_date >= date_from)
    if date_to is not None:
        filters.append(Fixture.match_date <= date_to)
    if status is not None:
        filters.append(Fixture.status_id == status)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Fixture.match_date.desc())

    items, meta = await paginate(db, query, page, per_page)

    return PaginatedResponse(
        items=[FixtureResponse.model_validate(fixture) for fixture in items],
        meta=meta,
    )


@router.get("/today", response_model=PaginatedResponse[FixtureResponse])
async def get_today_fixtures(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[FixtureResponse]:
    """Get today's fixtures.

    Args:
        db: Database session
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Returns:
        Paginated list of today's fixtures
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    query = (
        select(Fixture)
        .where(
            and_(
                Fixture.match_date >= today,
                Fixture.match_date < tomorrow,
            )
        )
        .order_by(Fixture.match_date)
    )

    items, meta = await paginate(db, query, page, per_page)

    return PaginatedResponse(
        items=[FixtureResponse.model_validate(fixture) for fixture in items],
        meta=meta,
    )


@router.get("/upcoming", response_model=PaginatedResponse[FixtureResponse])
async def get_upcoming_fixtures(
    db: Annotated[AsyncSession, Depends(get_db)],
    days: Annotated[int, Query(ge=1, le=30, description="Number of days ahead")] = 7,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[FixtureResponse]:
    """Get upcoming fixtures for the next N days.

    Args:
        db: Database session
        days: Number of days to look ahead (default: 7, max: 30)
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Returns:
        Paginated list of upcoming fixtures
    """
    now = datetime.now()
    future_date = now + timedelta(days=days)

    query = (
        select(Fixture)
        .where(
            and_(
                Fixture.match_date >= now,
                Fixture.match_date <= future_date,
            )
        )
        .order_by(Fixture.match_date)
    )

    items, meta = await paginate(db, query, page, per_page)

    return PaginatedResponse(
        items=[FixtureResponse.model_validate(fixture) for fixture in items],
        meta=meta,
    )


@router.get("/{fixture_id}", response_model=FixtureDetailResponse)
async def get_fixture_detail(
    fixture_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FixtureDetailResponse:
    """Get detailed fixture information including team details.

    Args:
        fixture_id: Fixture database ID
        db: Database session

    Returns:
        Detailed fixture information

    Raises:
        HTTPException: 404 if fixture not found
    """
    # Get fixture
    result = await db.execute(select(Fixture).where(Fixture.id == fixture_id))
    fixture = result.scalar_one_or_none()

    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")

    # Get home team
    home_team_result = await db.execute(
        select(Team).where(Team.team_id == fixture.home_team_id)
    )
    home_team = home_team_result.scalar_one_or_none()

    # Get away team
    away_team_result = await db.execute(
        select(Team).where(Team.team_id == fixture.away_team_id)
    )
    away_team = away_team_result.scalar_one_or_none()

    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="Team information not found")

    # Build response
    return FixtureDetailResponse(
        id=fixture.id,
        event_id=fixture.event_id,
        season_type=fixture.season_type,
        league_id=fixture.league_id,
        match_date=fixture.match_date,
        venue_id=fixture.venue_id,
        attendance=fixture.attendance,
        home_team=TeamInFixture(
            team_id=home_team.team_id,
            name=home_team.name,
            display_name=home_team.display_name,
            logo_url=home_team.logo_url,
            score=fixture.home_team_score,
            is_winner=fixture.home_team_winner,
        ),
        away_team=TeamInFixture(
            team_id=away_team.team_id,
            name=away_team.name,
            display_name=away_team.display_name,
            logo_url=away_team.logo_url,
            score=fixture.away_team_score,
            is_winner=fixture.away_team_winner,
        ),
        home_team_shootout_score=fixture.home_team_shootout_score,
        away_team_shootout_score=fixture.away_team_shootout_score,
        status_id=fixture.status_id,
        update_time=fixture.update_time,
        created_at=fixture.created_at,
    )
