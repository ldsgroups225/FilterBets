"""Statistics calculation service for teams."""


from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.team import Team
from app.models.team_stats import TeamStats
from app.schemas.team import TeamFormMatch, TeamFormResponse


async def calculate_team_form(
    session: AsyncSession,
    team_id: int,
    limit: int = 5,
) -> TeamFormResponse:
    """Calculate team form based on recent matches.

    Args:
        session: Database session
        team_id: Team ID to calculate form for
        limit: Number of recent matches to include (default: 5)

    Returns:
        Team form response with match history and statistics

    Raises:
        ValueError: If team not found
    """
    # Get team
    team_result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = team_result.scalar_one_or_none()

    if not team:
        raise ValueError(f"Team with ID {team_id} not found")

    # Get recent fixtures for this team (completed matches only)
    fixtures_query = (
        select(Fixture)
        .where(
            and_(
                or_(
                    Fixture.home_team_id == team_id,
                    Fixture.away_team_id == team_id,
                ),
                Fixture.status_id == 3,  # Completed matches
                Fixture.home_team_score.isnot(None),
                Fixture.away_team_score.isnot(None),
            )
        )
        .order_by(Fixture.match_date.desc())
        .limit(limit)
    )

    fixtures_result = await session.execute(fixtures_query)
    fixtures = list(fixtures_result.scalars().all())

    # Build form data
    matches: list[TeamFormMatch] = []
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    form_chars: list[str] = []

    for fixture in fixtures:
        is_home = fixture.home_team_id == team_id
        team_score = fixture.home_team_score if is_home else fixture.away_team_score
        opponent_score = fixture.away_team_score if is_home else fixture.home_team_score
        opponent_id = fixture.away_team_id if is_home else fixture.home_team_id

        # Get opponent name
        opponent_result = await session.execute(
            select(Team).where(Team.team_id == opponent_id)
        )
        opponent = opponent_result.scalar_one_or_none()
        opponent_name = opponent.display_name if opponent else "Unknown"

        # Determine result
        result = None
        if team_score is not None and opponent_score is not None:
            goals_for += team_score
            goals_against += opponent_score

            if team_score > opponent_score:
                result = "W"
                wins += 1
                form_chars.append("W")
            elif team_score < opponent_score:
                result = "L"
                losses += 1
                form_chars.append("L")
            else:
                result = "D"
                draws += 1
                form_chars.append("D")

        matches.append(
            TeamFormMatch(
                event_id=fixture.event_id,
                match_date=fixture.match_date,
                opponent_id=opponent_id,
                opponent_name=opponent_name,
                is_home=is_home,
                team_score=team_score,
                opponent_score=opponent_score,
                result=result,
            )
        )

    # Form string shows most recent first
    form_string = "".join(form_chars)

    return TeamFormResponse(
        team_id=team_id,
        team_name=team.display_name,
        matches=matches,
        wins=wins,
        draws=draws,
        losses=losses,
        goals_for=goals_for,
        goals_against=goals_against,
        form_string=form_string,
    )


async def get_head_to_head(
    session: AsyncSession,
    team1_id: int,
    team2_id: int,
    limit: int = 10,
) -> list[Fixture]:
    """Get head-to-head match history between two teams.

    Args:
        session: Database session
        team1_id: First team ID
        team2_id: Second team ID
        limit: Maximum number of matches to return (default: 10)

    Returns:
        List of fixtures between the two teams
    """
    query = (
        select(Fixture)
        .where(
            and_(
                or_(
                    and_(
                        Fixture.home_team_id == team1_id,
                        Fixture.away_team_id == team2_id,
                    ),
                    and_(
                        Fixture.home_team_id == team2_id,
                        Fixture.away_team_id == team1_id,
                    ),
                ),
                Fixture.status_id == 3,  # Completed matches only
            )
        )
        .order_by(Fixture.match_date.desc())
        .limit(limit)
    )

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_team_stats_for_match(
    session: AsyncSession,
    event_id: int,
    team_id: int,
) -> TeamStats | None:
    """Get team statistics for a specific match.

    Args:
        session: Database session
        event_id: Match/fixture ID
        team_id: Team ID

    Returns:
        Team statistics or None if not found
    """
    query = select(TeamStats).where(
        and_(
            TeamStats.event_id == event_id,
            TeamStats.team_id == team_id,
        )
    )

    result = await session.execute(query)
    return result.scalar_one_or_none()
