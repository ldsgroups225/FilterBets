"""Leagues API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.league import League
from app.models.team import Team
from app.schemas.common import PaginatedResponse
from app.schemas.league import LeagueResponse
from app.schemas.team import TeamResponse
from app.utils.pagination import paginate

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("", response_model=PaginatedResponse[LeagueResponse])
async def get_leagues(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[LeagueResponse]:
    """Get paginated list of leagues.

    Args:
        db: Database session
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Returns:
        Paginated list of leagues
    """
    query = select(League).order_by(League.league_name)
    items, meta = await paginate(db, query, page, per_page)

    return PaginatedResponse(
        items=[LeagueResponse.model_validate(league) for league in items],
        meta=meta,
    )


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
    league_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeagueResponse:
    """Get a single league by ID.

    Args:
        league_id: League database ID
        db: Database session

    Returns:
        League details

    Raises:
        HTTPException: 404 if league not found
    """
    result = await db.execute(select(League).where(League.id == league_id))
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    return LeagueResponse.model_validate(league)


@router.get("/{league_id}/teams", response_model=PaginatedResponse[TeamResponse])
async def get_league_teams(
    league_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[TeamResponse]:
    """Get teams in a specific league.

    Args:
        league_id: League database ID
        db: Database session
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Returns:
        Paginated list of teams in the league

    Raises:
        HTTPException: 404 if league not found
    """
    # Verify league exists
    league_result = await db.execute(select(League).where(League.id == league_id))
    league = league_result.scalar_one_or_none()

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    # Get teams - we'll need to join through fixtures or standings
    # For now, return all teams (we can filter by league later when we have league associations)
    query = select(Team).order_by(Team.display_name)
    items, meta = await paginate(db, query, page, per_page)

    return PaginatedResponse(
        items=[TeamResponse.model_validate(team) for team in items],
        meta=meta,
    )
