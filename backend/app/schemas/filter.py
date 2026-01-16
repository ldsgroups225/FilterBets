"""Filter schemas for request/response validation."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class FilterCondition(BaseModel):
    """A single filter condition."""

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
    """Schema for creating a new filter."""

    name: str = Field(..., min_length=1, max_length=100, description="Filter name")
    description: str | None = Field(None, max_length=500, description="Filter description")
    rules: list[FilterCondition] = Field(
        ..., min_length=1, max_length=10, description="Filter conditions (max 10)"
    )
    is_active: bool = Field(True, description="Whether filter is active")

    @field_validator("rules")
    @classmethod
    def validate_field_names(cls, v: list[FilterCondition]) -> list[FilterCondition]:
        """Validate that field names are allowed."""
        allowed_fields = {
            # Match context
            "league_id",
            "match_date",
            "status_id",
            "home_team_id",
            "away_team_id",
            # Scores
            "home_score",
            "away_score",
            "total_goals",
            # Home team computed stats
            "home_team_form_wins_last5",
            "home_team_form_wins_last10",
            "home_team_form_points_last5",
            "home_team_form_points_last10",
            "home_team_goals_avg",
            "home_team_goals_conceded_avg",
            "home_team_home_goals_avg",
            "home_team_clean_sheet_pct",
            "home_team_points_per_game",
            # Away team computed stats
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

        for condition in v:
            if condition.field not in allowed_fields:
                raise ValueError(
                    f"Invalid field name: {condition.field}. "
                    f"Allowed fields: {', '.join(sorted(allowed_fields))}"
                )

        return v


class FilterUpdate(BaseModel):
    """Schema for updating an existing filter."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    rules: list[FilterCondition] | None = Field(None, min_length=1, max_length=10)
    is_active: bool | None = None

    @field_validator("rules")
    @classmethod
    def validate_field_names(cls, v: list[FilterCondition] | None) -> list[FilterCondition] | None:
        """Validate that field names are allowed."""
        if v is None:
            return v

        allowed_fields = {
            "league_id",
            "match_date",
            "status_id",
            "home_team_id",
            "away_team_id",
            "home_score",
            "away_score",
            "total_goals",
            # Home team computed stats
            "home_team_form_wins_last5",
            "home_team_form_wins_last10",
            "home_team_form_points_last5",
            "home_team_form_points_last10",
            "home_team_goals_avg",
            "home_team_goals_conceded_avg",
            "home_team_home_goals_avg",
            "home_team_clean_sheet_pct",
            "home_team_points_per_game",
            # Away team computed stats
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

        for condition in v:
            if condition.field not in allowed_fields:
                raise ValueError(
                    f"Invalid field name: {condition.field}. "
                    f"Allowed fields: {', '.join(sorted(allowed_fields))}"
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
