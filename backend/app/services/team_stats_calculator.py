"""Team statistics calculator service for pre-computed stats."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.team import Team
from app.models.team_computed_stats import TeamComputedStats


class TeamStatsCalculator:
    """Service for calculating and storing pre-computed team statistics."""

    def __init__(self, session: AsyncSession):
        """Initialize the stats calculator.

        Args:
            session: Database session
        """
        self.session = session

    async def calculate_team_overall_stats(
        self, team_id: int, season_type: int
    ) -> dict:
        """Calculate overall team statistics for a season.

        Args:
            team_id: Team ID
            season_type: Season year

        Returns:
            Dictionary with overall stats
        """
        # Get all completed fixtures for this team in the season
        fixtures_query = select(Fixture).where(
            and_(
                or_(
                    Fixture.home_team_id == team_id,
                    Fixture.away_team_id == team_id,
                ),
                Fixture.season_type == season_type,
                Fixture.status_id == 3,  # Completed
                Fixture.home_team_score.isnot(None),
                Fixture.away_team_score.isnot(None),
            )
        )

        result = await self.session.execute(fixtures_query)
        fixtures = list(result.scalars().all())

        if not fixtures:
            return self._empty_overall_stats()

        matches_played = len(fixtures)
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        clean_sheets = 0
        failed_to_score = 0

        for fixture in fixtures:
            is_home = fixture.home_team_id == team_id
            team_score = (
                fixture.home_team_score if is_home else fixture.away_team_score
            )
            opponent_score = (
                fixture.away_team_score if is_home else fixture.home_team_score
            )

            goals_scored += team_score
            goals_conceded += opponent_score

            if opponent_score == 0:
                clean_sheets += 1
            if team_score == 0:
                failed_to_score += 1

            if team_score > opponent_score:
                wins += 1
            elif team_score < opponent_score:
                losses += 1
            else:
                draws += 1

        points = wins * 3 + draws

        return {
            "matches_played": matches_played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": goals_scored,
            "goals_conceded": goals_conceded,
            "goals_scored_avg": Decimal(str(goals_scored / matches_played)).quantize(
                Decimal("0.01")
            ),
            "goals_conceded_avg": Decimal(
                str(goals_conceded / matches_played)
            ).quantize(Decimal("0.01")),
            "clean_sheets": clean_sheets,
            "clean_sheet_pct": Decimal(
                str((clean_sheets / matches_played) * 100)
            ).quantize(Decimal("0.01")),
            "failed_to_score": failed_to_score,
            "failed_to_score_pct": Decimal(
                str((failed_to_score / matches_played) * 100)
            ).quantize(Decimal("0.01")),
            "points": points,
            "points_per_game": Decimal(str(points / matches_played)).quantize(
                Decimal("0.01")
            ),
        }

    async def calculate_team_home_stats(
        self, team_id: int, season_type: int
    ) -> dict:
        """Calculate home team statistics for a season.

        Args:
            team_id: Team ID
            season_type: Season year

        Returns:
            Dictionary with home stats
        """
        fixtures_query = select(Fixture).where(
            and_(
                Fixture.home_team_id == team_id,
                Fixture.season_type == season_type,
                Fixture.status_id == 3,
                Fixture.home_team_score.isnot(None),
                Fixture.away_team_score.isnot(None),
            )
        )

        result = await self.session.execute(fixtures_query)
        fixtures = list(result.scalars().all())

        if not fixtures:
            return self._empty_home_away_stats()

        home_matches = len(fixtures)
        home_wins = 0
        home_draws = 0
        home_losses = 0
        home_goals_scored = 0
        home_goals_conceded = 0

        for fixture in fixtures:
            home_goals_scored += fixture.home_team_score
            home_goals_conceded += fixture.away_team_score

            if fixture.home_team_score > fixture.away_team_score:
                home_wins += 1
            elif fixture.home_team_score < fixture.away_team_score:
                home_losses += 1
            else:
                home_draws += 1

        return {
            "home_matches": home_matches,
            "home_wins": home_wins,
            "home_draws": home_draws,
            "home_losses": home_losses,
            "home_goals_scored_avg": Decimal(
                str(home_goals_scored / home_matches)
            ).quantize(Decimal("0.01")),
            "home_goals_conceded_avg": Decimal(
                str(home_goals_conceded / home_matches)
            ).quantize(Decimal("0.01")),
        }

    async def calculate_team_away_stats(
        self, team_id: int, season_type: int
    ) -> dict:
        """Calculate away team statistics for a season.

        Args:
            team_id: Team ID
            season_type: Season year

        Returns:
            Dictionary with away stats
        """
        fixtures_query = select(Fixture).where(
            and_(
                Fixture.away_team_id == team_id,
                Fixture.season_type == season_type,
                Fixture.status_id == 3,
                Fixture.home_team_score.isnot(None),
                Fixture.away_team_score.isnot(None),
            )
        )

        result = await self.session.execute(fixtures_query)
        fixtures = list(result.scalars().all())

        if not fixtures:
            return self._empty_home_away_stats()

        away_matches = len(fixtures)
        away_wins = 0
        away_draws = 0
        away_losses = 0
        away_goals_scored = 0
        away_goals_conceded = 0

        for fixture in fixtures:
            away_goals_scored += fixture.away_team_score
            away_goals_conceded += fixture.home_team_score

            if fixture.away_team_score > fixture.home_team_score:
                away_wins += 1
            elif fixture.away_team_score < fixture.home_team_score:
                away_losses += 1
            else:
                away_draws += 1

        return {
            "away_matches": away_matches,
            "away_wins": away_wins,
            "away_draws": away_draws,
            "away_losses": away_losses,
            "away_goals_scored_avg": Decimal(
                str(away_goals_scored / away_matches)
            ).quantize(Decimal("0.01")),
            "away_goals_conceded_avg": Decimal(
                str(away_goals_conceded / away_matches)
            ).quantize(Decimal("0.01")),
        }

    async def calculate_team_form(
        self, team_id: int, season_type: int, n_games: int
    ) -> dict:
        """Calculate team form for last N games.

        Args:
            team_id: Team ID
            season_type: Season year
            n_games: Number of recent games (5 or 10)

        Returns:
            Dictionary with form stats
        """
        fixtures_query = (
            select(Fixture)
            .where(
                and_(
                    or_(
                        Fixture.home_team_id == team_id,
                        Fixture.away_team_id == team_id,
                    ),
                    Fixture.season_type == season_type,
                    Fixture.status_id == 3,
                    Fixture.home_team_score.isnot(None),
                    Fixture.away_team_score.isnot(None),
                )
            )
            .order_by(Fixture.match_date.desc())
            .limit(n_games)
        )

        result = await self.session.execute(fixtures_query)
        fixtures = list(result.scalars().all())

        if not fixtures:
            return self._empty_form_stats(n_games)

        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0

        for fixture in fixtures:
            is_home = fixture.home_team_id == team_id
            team_score = (
                fixture.home_team_score if is_home else fixture.away_team_score
            )
            opponent_score = (
                fixture.away_team_score if is_home else fixture.home_team_score
            )

            goals_scored += team_score
            goals_conceded += opponent_score

            if team_score > opponent_score:
                wins += 1
            elif team_score < opponent_score:
                losses += 1
            else:
                draws += 1

        points = wins * 3 + draws

        prefix = f"form_last{n_games}_"
        stats = {
            f"{prefix}wins": wins,
            f"{prefix}draws": draws,
            f"{prefix}losses": losses,
            f"{prefix}points": points,
        }

        # Only include goals for last 5
        if n_games == 5:
            stats[f"{prefix}goals_scored"] = goals_scored
            stats[f"{prefix}goals_conceded"] = goals_conceded

        return stats

    async def refresh_team_stats(self, team_id: int, season_type: int) -> TeamComputedStats:
        """Refresh computed stats for a specific team and season.

        Args:
            team_id: Team ID
            season_type: Season year

        Returns:
            Updated TeamComputedStats instance
        """
        # Calculate all stats
        overall_stats = await self.calculate_team_overall_stats(team_id, season_type)
        home_stats = await self.calculate_team_home_stats(team_id, season_type)
        away_stats = await self.calculate_team_away_stats(team_id, season_type)
        form_last5 = await self.calculate_team_form(team_id, season_type, 5)
        form_last10 = await self.calculate_team_form(team_id, season_type, 10)

        # Merge all stats
        all_stats = {
            **overall_stats,
            **home_stats,
            **away_stats,
            **form_last5,
            **form_last10,
        }

        # Check if record exists
        query = select(TeamComputedStats).where(
            and_(
                TeamComputedStats.team_id == team_id,
                TeamComputedStats.season_type == season_type,
            )
        )
        result = await self.session.execute(query)
        computed_stats = result.scalar_one_or_none()

        if computed_stats:
            # Update existing
            for key, value in all_stats.items():
                setattr(computed_stats, key, value)
            computed_stats.computed_at = datetime.utcnow()
        else:
            # Create new
            computed_stats = TeamComputedStats(
                team_id=team_id,
                season_type=season_type,
                computed_at=datetime.utcnow(),
                **all_stats,
            )
            self.session.add(computed_stats)

        await self.session.commit()
        await self.session.refresh(computed_stats)

        return computed_stats

    async def refresh_all_team_stats(self, season_type: int | None = None) -> int:
        """Refresh computed stats for all teams.

        Args:
            season_type: Optional season year to refresh (defaults to all seasons)

        Returns:
            Number of team stats refreshed
        """
        # Get all teams
        teams_query = select(Team)
        result = await self.session.execute(teams_query)
        teams = list(result.scalars().all())

        # Get distinct seasons from fixtures
        if season_type:
            seasons = [season_type]
        else:
            seasons_query = select(Fixture.season_type).distinct()
            seasons_result = await self.session.execute(seasons_query)
            seasons = [s for s in seasons_result.scalars().all() if s is not None]

        count = 0
        for team in teams:
            for season in seasons:
                await self.refresh_team_stats(team.team_id, season)
                count += 1

        return count

    def _empty_overall_stats(self) -> dict:
        """Return empty overall stats."""
        return {
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "goals_scored_avg": Decimal("0.00"),
            "goals_conceded_avg": Decimal("0.00"),
            "clean_sheets": 0,
            "clean_sheet_pct": Decimal("0.00"),
            "failed_to_score": 0,
            "failed_to_score_pct": Decimal("0.00"),
            "points": 0,
            "points_per_game": Decimal("0.00"),
        }

    def _empty_home_away_stats(self) -> dict:
        """Return empty home/away stats."""
        return {
            "home_matches": 0,
            "home_wins": 0,
            "home_draws": 0,
            "home_losses": 0,
            "home_goals_scored_avg": Decimal("0.00"),
            "home_goals_conceded_avg": Decimal("0.00"),
            "away_matches": 0,
            "away_wins": 0,
            "away_draws": 0,
            "away_losses": 0,
            "away_goals_scored_avg": Decimal("0.00"),
            "away_goals_conceded_avg": Decimal("0.00"),
        }

    def _empty_form_stats(self, n_games: int) -> dict:
        """Return empty form stats."""
        prefix = f"form_last{n_games}_"
        stats = {
            f"{prefix}wins": 0,
            f"{prefix}draws": 0,
            f"{prefix}losses": 0,
            f"{prefix}points": 0,
        }
        if n_games == 5:
            stats[f"{prefix}goals_scored"] = 0
            stats[f"{prefix}goals_conceded"] = 0
        return stats
