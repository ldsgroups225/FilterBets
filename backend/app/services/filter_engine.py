"""Filter engine for matching fixtures against filter rules."""

from datetime import date
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.models.fixture import Fixture
from app.models.team_computed_stats import TeamComputedStats


class FilterEngine:
    """Engine for evaluating filter rules against fixtures."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_matching_fixtures(
        self,
        rules: list[dict[str, Any]],
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 100,
        eager_load_relations: bool = True,
    ) -> list[Fixture]:
        """
        Find fixtures that match all filter conditions.

        Args:
            rules: List of filter conditions
            date_from: Optional start date filter
            date_to: Optional end date filter
            limit: Maximum number of results
            eager_load_relations: Whether to eagerly load related entities

        Returns:
            List of matching fixtures
        """
        needs_stats_join = self._needs_stats_join(rules)

        if needs_stats_join:
            home_stats = aliased(TeamComputedStats)
            away_stats = aliased(TeamComputedStats)

            query = (
                select(Fixture)
                .outerjoin(
                    home_stats,
                    and_(
                        home_stats.team_id == Fixture.home_team_id,
                        home_stats.season_type == Fixture.season_type,
                    ),
                )
                .outerjoin(
                    away_stats,
                    and_(
                        away_stats.team_id == Fixture.away_team_id,
                        away_stats.season_type == Fixture.season_type,
                    ),
                )
            )
        else:
            query = select(Fixture)
            home_stats = None
            away_stats = None

        conditions = []
        if date_from:
            conditions.append(Fixture.match_date >= date_from)
        if date_to:
            conditions.append(Fixture.match_date <= date_to)

        for rule in rules:
            field = rule["field"]
            operator = rule["operator"]
            value = rule["value"]

            condition = self._build_condition(
                field, operator, value, home_stats, away_stats
            )
            if condition is not None:
                conditions.append(condition)

        if conditions:
            query = query.where(and_(*conditions))

        if eager_load_relations:
            query = query.options(
                selectinload(Fixture.home_team),
                selectinload(Fixture.away_team),
                selectinload(Fixture.league),
            )

        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _needs_stats_join(self, rules: list[dict[str, Any]]) -> bool:
        """Check if any rules require team_computed_stats join."""
        stats_fields = {
            "home_team_form_wins_last5",
            "home_team_form_wins_last10",
            "home_team_form_points_last5",
            "home_team_form_points_last10",
            "home_team_goals_avg",
            "home_team_goals_conceded_avg",
            "home_team_home_goals_avg",
            "home_team_clean_sheet_pct",
            "home_team_points_per_game",
            "away_team_form_wins_last5",
            "away_team_form_wins_last10",
            "away_team_form_points_last5",
            "away_team_form_points_last10",
            "away_team_goals_avg",
            "away_team_goals_conceded_avg",
            "away_team_away_goals_avg",
            "away_team_clean_sheet_pct",
            "away_team_points_per_game",
            "total_expected_goals",
        }

        return any(rule["field"] in stats_fields for rule in rules)

    def _build_condition(
        self,
        field: str,
        operator: str,
        value: Any,
        home_stats: Any = None,
        away_stats: Any = None,
    ) -> Any:
        """
        Build SQLAlchemy condition for a single filter rule.

        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare
            home_stats: Home team stats alias (if joined)
            away_stats: Away team stats alias (if joined)

        Returns:
            SQLAlchemy condition or None if field not supported
        """
        # Map field names to model attributes
        field_map = {
            "league_id": Fixture.league_id,
            "match_date": Fixture.match_date,
            "status_id": Fixture.status_id,
            "home_score": Fixture.home_team_score,
            "away_score": Fixture.away_team_score,
            "home_team_id": Fixture.home_team_id,
            "away_team_id": Fixture.away_team_id,
        }

        # Get the model attribute
        if field in field_map:
            attr = field_map[field]
        elif field.startswith("home_team_") and home_stats is not None:
            # Home team computed stats
            attr = self._get_stats_attribute(field, home_stats, "home")
            if attr is None:
                return None
        elif field.startswith("away_team_") and away_stats is not None:
            # Away team computed stats
            attr = self._get_stats_attribute(field, away_stats, "away")
            if attr is None:
                return None
        elif field == "total_expected_goals" and home_stats and away_stats:
            # Computed field: sum of home and away goals averages
            return self._build_operator_condition(
                home_stats.home_goals_scored_avg + away_stats.away_goals_scored_avg,
                operator,
                value,
            )
        else:
            # Field not supported
            return None

        # Build condition based on operator
        return self._build_operator_condition(attr, operator, value)

    def _get_stats_attribute(self, field: str, stats_alias: Any, team_type: str) -> Any:
        """Get the appropriate stats attribute for a field.

        Args:
            field: Field name (e.g., "home_team_goals_avg")
            stats_alias: TeamComputedStats alias
            team_type: "home" or "away"

        Returns:
            SQLAlchemy attribute or None
        """
        # Map filter field names to TeamComputedStats attributes
        stats_map = {
            f"{team_type}_team_form_wins_last5": stats_alias.form_last5_wins,
            f"{team_type}_team_form_wins_last10": stats_alias.form_last10_wins,
            f"{team_type}_team_form_points_last5": stats_alias.form_last5_points,
            f"{team_type}_team_form_points_last10": stats_alias.form_last10_points,
            f"{team_type}_team_goals_avg": stats_alias.goals_scored_avg,
            f"{team_type}_team_goals_conceded_avg": stats_alias.goals_conceded_avg,
            f"{team_type}_team_clean_sheet_pct": stats_alias.clean_sheet_pct,
            f"{team_type}_team_points_per_game": stats_alias.points_per_game,
        }

        # Special handling for home/away specific stats
        if team_type == "home":
            stats_map[f"{team_type}_team_home_goals_avg"] = stats_alias.home_goals_scored_avg
        elif team_type == "away":
            stats_map[f"{team_type}_team_away_goals_avg"] = stats_alias.away_goals_scored_avg

        return stats_map.get(field)

    def _build_operator_condition(self, attr: Any, operator: str, value: Any) -> Any:
        """Build condition based on operator.

        Args:
            attr: SQLAlchemy attribute
            operator: Comparison operator
            value: Value to compare

        Returns:
            SQLAlchemy condition
        """
        if operator == "=":
            return attr == value
        elif operator == "!=":
            return attr != value
        elif operator == ">":
            return attr > value
        elif operator == "<":
            return attr < value
        elif operator == ">=":
            return attr >= value
        elif operator == "<=":
            return attr <= value
        elif operator == "in":
            return attr.in_(value)
        elif operator == "between":
            return and_(attr >= value[0], attr <= value[1])

        return None

    def evaluate_fixture(self, fixture: Fixture, rules: list[dict[str, Any]]) -> bool:
        """
        Evaluate if a single fixture matches all filter rules.

        Args:
            fixture: Fixture to evaluate
            rules: List of filter conditions

        Returns:
            True if fixture matches all conditions
        """
        for rule in rules:
            field = rule["field"]
            operator = rule["operator"]
            value = rule["value"]

            if not self._evaluate_condition(fixture, field, operator, value):
                return False

        return True

    def _evaluate_condition(
        self, fixture: Fixture, field: str, operator: str, value: Any
    ) -> bool:
        """
        Evaluate a single condition against a fixture.

        Args:
            fixture: Fixture to evaluate
            field: Field name
            operator: Comparison operator
            value: Value to compare

        Returns:
            True if condition matches
        """
        # Get field value from fixture
        field_value = self._get_field_value(fixture, field)
        if field_value is None:
            return False

        # Evaluate based on operator
        if operator == "=":
            return bool(field_value == value)
        elif operator == "!=":
            return bool(field_value != value)
        elif operator == ">":
            return bool(field_value > value)
        elif operator == "<":
            return bool(field_value < value)
        elif operator == ">=":
            return bool(field_value >= value)
        elif operator == "<=":
            return bool(field_value <= value)
        elif operator == "in":
            return bool(field_value in value)
        elif operator == "between":
            return bool(value[0] <= field_value <= value[1])

        return False

    def _get_field_value(self, fixture: Fixture, field: str) -> Any:
        """
        Get field value from fixture.

        Note: This method is for in-memory evaluation and doesn't support
        computed stats fields that require database joins. Use find_matching_fixtures
        for queries with computed stats.

        Args:
            fixture: Fixture object
            field: Field name

        Returns:
            Field value or None if not found
        """
        # Direct fixture fields
        direct_fields = {
            "league_id": fixture.league_id,
            "match_date": fixture.match_date,
            "status_id": fixture.status_id,
            "home_score": fixture.home_team_score,
            "away_score": fixture.away_team_score,
            "home_team_id": fixture.home_team_id,
            "away_team_id": fixture.away_team_id,
        }

        if field in direct_fields:
            return direct_fields[field]

        # Calculated fields
        if field == "total_goals":
            if fixture.home_team_score is not None and fixture.away_team_score is not None:
                return fixture.home_team_score + fixture.away_team_score
            return None

        # Team stats fields require database queries and are not supported
        # in in-memory evaluation. Use find_matching_fixtures instead.
        return None
