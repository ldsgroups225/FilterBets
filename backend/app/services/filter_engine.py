"""Filter engine for matching fixtures against filter rules."""

from datetime import date
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture


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
    ) -> list[Fixture]:
        """
        Find fixtures that match all filter conditions.

        Args:
            rules: List of filter conditions
            date_from: Optional start date filter
            date_to: Optional end date filter
            limit: Maximum number of results

        Returns:
            List of matching fixtures
        """
        # Build base query
        query = select(Fixture)

        # Add date range filters
        conditions = []
        if date_from:
            conditions.append(Fixture.match_date >= date_from)
        if date_to:
            conditions.append(Fixture.match_date <= date_to)

        # Parse and apply filter rules
        for rule in rules:
            field = rule["field"]
            operator = rule["operator"]
            value = rule["value"]

            condition = self._build_condition(field, operator, value)
            if condition is not None:
                conditions.append(condition)

        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Execute query
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _build_condition(self, field: str, operator: str, value: Any) -> Any:
        """
        Build SQLAlchemy condition for a single filter rule.

        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare

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
        else:
            # Fields not directly on Fixture model (e.g., team stats, odds)
            # These would require joins - not implemented in this basic version
            return None

        # Build condition based on operator
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
            return field_value == value
        elif operator == "!=":
            return field_value != value
        elif operator == ">":
            return field_value > value
        elif operator == "<":
            return field_value < value
        elif operator == ">=":
            return field_value >= value
        elif operator == "<=":
            return field_value <= value
        elif operator == "in":
            return field_value in value
        elif operator == "between":
            return value[0] <= field_value <= value[1]

        return False

    def _get_field_value(self, fixture: Fixture, field: str) -> Any:
        """
        Get field value from fixture.

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

        # Team stats fields would require additional queries
        # Not implemented in this basic version
        return None
