"""Teams API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.team import Team
from app.schemas.fixture import FixtureResponse
from app.schemas.team import TeamFormResponse, TeamResponse, TeamStatsResponse
from app.services.stats_calculator import (
    calculate_team_form,
    get_head_to_head,
    get_team_stats_for_match,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamResponse:
    """Get a single team by ID.

    Args:
        team_id: Team ESPN ID
        db: Database session

    Returns:
        Team details

    Raises:
        HTTPException: 404 if team not found
    """
    result = await db.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return TeamResponse.model_validate(team)


@router.get("/{team_id}/stats/{event_id}", response_model=TeamStatsResponse)
async def get_team_match_stats(
    team_id: int,
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamStatsResponse:
    """Get team statistics for a specific match.

    Args:
        team_id: Team ESPN ID
        event_id: Match/fixture ID
        db: Database session

    Returns:
        Team statistics for the match

    Raises:
        HTTPException: 404 if stats not found
    """
    stats = await get_team_stats_for_match(db, event_id, team_id)

    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Stats not found for team {team_id} in match {event_id}",
        )

    return TeamStatsResponse.model_validate(stats)


@router.get("/{team_id}/form", response_model=TeamFormResponse)
async def get_team_form(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> TeamFormResponse:
    """Get team form based on recent matches.

    Args:
        team_id: Team ESPN ID
        db: Database session
        limit: Number of recent matches to include (default: 5, max: 20)

    Returns:
        Team form with match history and statistics

    Raises:
        HTTPException: 404 if team not found
    """
    try:
        form = await calculate_team_form(db, team_id, limit)
        return form
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/head-to-head/{team1_id}/{team2_id}", response_model=list[FixtureResponse])
async def get_head_to_head_matches(
    team1_id: int,
    team2_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[FixtureResponse]:
    """Get head-to-head match history between two teams.

    Args:
        team1_id: First team ESPN ID
        team2_id: Second team ESPN ID
        db: Database session
        limit: Maximum number of matches to return (default: 10, max: 50)

    Returns:
        List of fixtures between the two teams
    """
    fixtures = await get_head_to_head(db, team1_id, team2_id, limit)

    return [FixtureResponse.model_validate(fixture) for fixture in fixtures]
