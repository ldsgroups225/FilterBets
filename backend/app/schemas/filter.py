"""Filter schemas for request/response validation.

This module defines schemas for creating and managing filter strategies.
Important: Filters should use PRE-MATCH data only to avoid look-ahead bias.
See POST_MATCH_FIELDS below for fields that CANNOT be used in filters.
"""

from datetime import datetime
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field, field_validator


class FieldInfo(TypedDict):
    """Information about a filter field."""

    alternative: str | None
    description: str


POST_MATCH_FIELDS: dict[str, FieldInfo] = {
    "home_score": {
        "alternative": "home_team_goals_avg",
        "description": "Use average goals scored by home team instead"
    },
    "away_score": {
        "alternative": "away_team_goals_avg",
        "description": "Use average goals scored by away team instead"
    },
    "total_goals": {
        "alternative": "total_expected_goals",
        "description": "Use expected goals (sum of home and away averages) instead"
    },
    "home_team_winner": {
        "alternative": "home_team_form_points_last5",
        "description": "Use recent form points instead of match outcome"
    },
    "away_team_winner": {
        "alternative": "away_team_form_points_last5",
        "description": "Use recent form points instead of match outcome"
    },
    "home_team_shootout_score": {
        "alternative": None,
        "description": "Penalty shootout data is always post-match"
    },
    "away_team_shootout_score": {
        "alternative": None,
        "description": "Penalty shootout data is always post-match"
    },
    "home_clean_sheet": {
        "alternative": "home_team_clean_sheet_pct",
        "description": "Use historical clean sheet percentage instead"
    },
    "away_clean_sheet": {
        "alternative": "away_team_clean_sheet_pct",
        "description": "Use historical clean sheet percentage instead"
    },
}

PRE_MATCH_ONLY_FIELDS = {
    # Match context (available before match)
    "league_id",
    "match_date",
    "status_id",
    "home_team_id",
    "away_team_id",
    "venue_id",
    # Pre-match team stats
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
    # Computed fields
    "total_expected_goals",
}


class FilterCondition(BaseModel):
    """A single filter condition.

    Note: Fields in POST_MATCH_FIELDS will be rejected to prevent look-ahead bias.
    Use the pre-match alternatives listed in POST_MATCH_FIELDS instead.
    """

    field: str = Field(..., description="Field name to filter on")
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "in", "between"] = Field(
        ..., description="Comparison operator"
    )
    value: Any = Field(..., description="Value to compare against")

    @field_validator("value")
    @classmethod
    def validate_value_for_operator(cls, v: Any, info: Any) -> Any:
        """Validate value matches operator requirements."""
        operator = info.data.get("operator")
        if operator == "in" and not isinstance(v, list):
            raise ValueError("Value must be a list for 'in' operator")
        if operator == "between" and (not isinstance(v, list) or len(v) != 2):
            raise ValueError("Value must be a list of 2 elements for 'between' operator")
        return v


class FilterCreate(BaseModel):
    """Schema for creating a new filter.

    Filters should use PRE-MATCH data only. Using post-match fields
    (like scores or outcomes) creates look-ahead bias and invalidates
    backtest results.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Filter name")
    description: str | None = Field(None, max_length=500, description="Filter description")
    rules: list[FilterCondition] = Field(
        ..., min_length=1, max_length=10, description="Filter conditions (max 10)"
    )
    is_active: bool = Field(True, description="Whether filter is active")

    @field_validator("rules")
    @classmethod
    def validate_no_look_ahead_bias(cls, v: list[FilterCondition]) -> list[FilterCondition]:
        """Reject filters that use post-match data (look-ahead bias prevention)."""
        errors = []

        for condition in v:
            if condition.field in POST_MATCH_FIELDS:
                info = POST_MATCH_FIELDS[condition.field]
                if info["alternative"]:
                    error_msg = (
                        f"Cannot filter by '{condition.field}' - this is post-match data. "
                        f"Use pre-match alternative '{info['alternative']}' instead: {info['description']}"
                    )
                else:
                    error_msg = (
                        f"Cannot filter by '{condition.field}' - this is post-match data. "
                        f"There is no pre-match alternative available."
                    )
                errors.append(error_msg)

        if errors:
            raise ValueError("\n".join(errors))

        return v

    @field_validator("rules")
    @classmethod
    def validate_field_names(cls, v: list[FilterCondition]) -> list[FilterCondition]:
        """Validate that field names are allowed (pre-match only)."""
        for condition in v:
            if condition.field not in PRE_MATCH_ONLY_FIELDS:
                if condition.field in POST_MATCH_FIELDS:
                    info = POST_MATCH_FIELDS[condition.field]
                    alt = info["alternative"] or "no pre-match alternative"
                    raise ValueError(
                        f"Cannot use '{condition.field}' (post-match). "
                        f"Use '{alt}' instead."
                    )
                raise ValueError(
                    f"Invalid field name: '{condition.field}'. "
                    f"Allowed pre-match fields: {', '.join(sorted(PRE_MATCH_ONLY_FIELDS))}"
                )

        return v


class FilterUpdate(BaseModel):
    """Schema for updating an existing filter.

    Same look-ahead bias restrictions apply as FilterCreate.
    """

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    rules: list[FilterCondition] | None = Field(None, min_length=1, max_length=10)
    is_active: bool | None = None

    @field_validator("rules")
    @classmethod
    def validate_no_look_ahead_bias(cls, v: list[FilterCondition] | None) -> list[FilterCondition] | None:
        """Reject filters that use post-match data (look-ahead bias prevention)."""
        if v is None:
            return v

        errors = []

        for condition in v:
            if condition.field in POST_MATCH_FIELDS:
                info = POST_MATCH_FIELDS[condition.field]
                if info["alternative"]:
                    error_msg = (
                        f"Cannot filter by '{condition.field}' - this is post-match data. "
                        f"Use pre-match alternative '{info['alternative']}' instead."
                    )
                else:
                    error_msg = (
                        f"Cannot filter by '{condition.field}' - this is post-match data. "
                        f"There is no pre-match alternative available."
                    )
                errors.append(error_msg)

        if errors:
            raise ValueError("\n".join(errors))

        return v

    @field_validator("rules")
    @classmethod
    def validate_field_names(cls, v: list[FilterCondition] | None) -> list[FilterCondition] | None:
        """Validate that field names are allowed (pre-match only)."""
        if v is None:
            return v

        for condition in v:
            if condition.field not in PRE_MATCH_ONLY_FIELDS:
                if condition.field in POST_MATCH_FIELDS:
                    info = POST_MATCH_FIELDS[condition.field]
                    alt = info["alternative"] or "no pre-match alternative"
                    raise ValueError(
                        f"Cannot use '{condition.field}' (post-match). "
                        f"Use '{alt}' instead."
                    )
                raise ValueError(
                    f"Invalid field name: '{condition.field}'. "
                    f"Allowed pre-match fields: {', '.join(sorted(PRE_MATCH_ONLY_FIELDS))}"
                )

        return v


class FilterAlertsToggle(BaseModel):
    """Schema for toggling filter alerts."""

    alerts_enabled: bool = Field(..., description="Enable or disable alerts")


class FilterResponse(BaseModel):
    """Schema for filter response."""

    id: int
    user_id: int
    name: str
    description: str | None
    rules: list[dict[str, Any]]  # JSONB stored as dict
    is_active: bool
    alerts_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
