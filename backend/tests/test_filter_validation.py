"""Tests for filter validation, especially look-ahead bias prevention."""

import pytest
from pydantic import ValidationError

from app.schemas.filter import (
    FilterCreate,
    FilterUpdate,
    POST_MATCH_FIELDS,
    PRE_MATCH_ONLY_FIELDS,
)


class TestPostMatchFields:
    """Test that post-match fields are properly identified."""

    def test_all_post_match_fields_identified(self):
        """Verify all known post-match fields are in the constant."""
        expected = {
            "home_score", "away_score", "total_goals",
            "home_team_winner", "away_team_winner",
            "home_team_shootout_score", "away_team_shootout_score",
            "home_clean_sheet", "away_clean_sheet",
        }
        assert set(POST_MATCH_FIELDS.keys()) == expected

    def test_post_match_fields_have_alternatives(self):
        """Verify most post-match fields have pre-match alternatives."""
        for field, info in POST_MATCH_FIELDS.items():
            if info["alternative"] is None:
                assert field in ["home_team_shootout_score", "away_team_shootout_score"]
            else:
                assert info["alternative"] in PRE_MATCH_ONLY_FIELDS


class TestFilterCreateLookAheadBias:
    """Test FilterCreate rejects post-match fields."""

    @pytest.mark.parametrize("field", POST_MATCH_FIELDS.keys())
    def test_rejects_all_post_match_fields(self, field):
        """Each post-match field should be rejected."""
        filter_data = {
            "name": "Test Filter",
            "rules": [{"field": field, "operator": "=", "value": 1}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        assert "post-match data" in str(exc_info.value).lower()

    def test_rejects_home_score(self):
        """home_score is post-match data."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "home_score", "operator": ">=", "value": 2}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        error_msg = str(exc_info.value)
        assert "home_team_goals_avg" in error_msg

    def test_rejects_total_goals(self):
        """total_goals is post-match data."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "total_goals", "operator": ">=", "value": 2.5}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        error_msg = str(exc_info.value)
        assert "total_expected_goals" in error_msg

    def test_rejects_shootout_score(self):
        """shootout scores have no pre-match alternative."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "home_team_shootout_score", "operator": "=", "value": 3}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        error_msg = str(exc_info.value)
        assert "no pre-match alternative" in error_msg.lower()


class TestFilterCreateValidFields:
    """Test FilterCreate accepts valid pre-match fields."""

    def test_accepts_league_id(self):
        """league_id is pre-match data."""
        filter_data = {
            "name": "Test Filter",
            "rules": [{"field": "league_id", "operator": "=", "value": 745}]
        }
        filter_obj = FilterCreate(**filter_data)
        assert filter_obj.name == "Test Filter"
        assert len(filter_obj.rules) == 1

    def test_accepts_home_team_stats(self):
        """Home team computed stats are pre-match data."""
        filter_data = {
            "name": "High Scoring Home",
            "rules": [
                {"field": "home_team_goals_avg", "operator": ">=", "value": 1.5},
                {"field": "home_team_form_points_last5", "operator": ">=", "value": 10}
            ]
        }
        filter_obj = FilterCreate(**filter_data)
        assert filter_obj.name == "High Scoring Home"
        assert len(filter_obj.rules) == 2

    def test_accepts_away_team_stats(self):
        """Away team computed stats are pre-match data."""
        filter_data = {
            "name": "Weak Away Defense",
            "rules": [
                {"field": "away_team_goals_conceded_avg", "operator": ">=", "value": 1.3}
            ]
        }
        filter_obj = FilterCreate(**filter_data)
        assert filter_obj.name == "Weak Away Defense"

    def test_accepts_total_expected_goals(self):
        """total_expected_goals is a valid pre-match computed field."""
        filter_data = {
            "name": "High Expected Goals",
            "rules": [{"field": "total_expected_goals", "operator": ">=", "value": 2.5}]
        }
        filter_obj = FilterCreate(**filter_data)
        assert filter_obj.name == "High Expected Goals"

    def test_accepts_multiple_rules(self):
        """Multiple rules with valid fields should work."""
        filter_data = {
            "name": "Comprehensive Filter",
            "rules": [
                {"field": "league_id", "operator": "in", "value": [745, 630]},
                {"field": "home_team_goals_avg", "operator": ">=", "value": 1.5},
                {"field": "away_team_goals_conceded_avg", "operator": ">=", "value": 1.2},
                {"field": "home_team_form_points_last5", "operator": ">=", "value": 9}
            ]
        }
        filter_obj = FilterCreate(**filter_data)
        assert len(filter_obj.rules) == 4

    def test_rejects_invalid_field(self):
        """Non-existent fields should be rejected."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "made_up_field", "operator": "=", "value": 1}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        error_msg = str(exc_info.value)
        assert "Invalid field name" in error_msg


class TestFilterUpdateLookAheadBias:
    """Test FilterUpdate also rejects post-match fields."""

    def test_rejects_post_match_field_in_update(self):
        """Updates with post-match fields should fail."""
        update_data = {
            "rules": [{"field": "home_score", "operator": ">=", "value": 2}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterUpdate(**update_data)
        assert "post-match data" in str(exc_info.value).lower()

    def test_allows_valid_update(self):
        """Updates with valid fields should work."""
        update_data = {
            "name": "Updated Filter",
            "rules": [{"field": "home_team_goals_avg", "operator": ">=", "value": 1.8}]
        }
        update_obj = FilterUpdate(**update_data)
        assert update_obj.name == "Updated Filter"
        assert len(update_obj.rules) == 1

    def test_allows_none_rules(self):
        """None rules should pass (partial update)."""
        update_data = {"name": "Name Only Update"}
        update_obj = FilterUpdate(**update_data)
        assert update_obj.name == "Name Only Update"
        assert update_obj.rules is None


class TestFilterConditionValidation:
    """Test FilterCondition value validation."""

    def test_rejects_invalid_operator_value_combo(self):
        """'in' operator requires a list value."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "league_id", "operator": "in", "value": 745}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        assert "must be a list" in str(exc_info.value).lower()

    def test_rejects_between_wrong_length(self):
        """'between' operator requires exactly 2 values."""
        filter_data = {
            "name": "Bad Filter",
            "rules": [{"field": "home_team_goals_avg", "operator": "between", "value": [1]}]
        }
        with pytest.raises(ValidationError) as exc_info:
            FilterCreate(**filter_data)
        assert "list of 2 elements" in str(exc_info.value).lower()

    def test_accepts_between_correct_length(self):
        """'between' operator with 2 values should work."""
        filter_data = {
            "name": "Range Filter",
            "rules": [{"field": "home_team_goals_avg", "operator": "between", "value": [1.0, 2.0]}]
        }
        filter_obj = FilterCreate(**filter_data)
        assert filter_obj.rules[0].value == [1.0, 2.0]


class TestFilterSchemaBoundaries:
    """Test schema boundary conditions."""

    def test_rejects_empty_rules(self):
        """Empty rules list should fail."""
        filter_data = {
            "name": "Empty Filter",
            "rules": []
        }
        with pytest.raises(ValidationError):
            FilterCreate(**filter_data)

    def test_rejects_too_many_rules(self):
        """More than 10 rules should fail."""
        rules = [{"field": "league_id", "operator": "=", "value": 1} for _ in range(11)]
        filter_data = {"name": "Too Many Rules", "rules": rules}
        with pytest.raises(ValidationError):
            FilterCreate(**filter_data)

    def test_name_max_length(self):
        """Name over 100 chars should fail."""
        filter_data = {
            "name": "x" * 101,
            "rules": [{"field": "league_id", "operator": "=", "value": 1}]
        }
        with pytest.raises(ValidationError):
            FilterCreate(**filter_data)
