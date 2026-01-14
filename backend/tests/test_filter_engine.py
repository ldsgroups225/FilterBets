"""Unit tests for filter engine."""

from datetime import date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.services.filter_engine import FilterEngine


@pytest.mark.asyncio
class TestFilterEngineEvaluation:
    """Test filter engine evaluation logic (no database required)."""

    async def test_evaluate_fixture_equals(self):
        """Test evaluating fixture with equals operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "league_id", "operator": "=", "value": 1}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_not_equals(self):
        """Test evaluating fixture with not equals operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "league_id", "operator": "!=", "value": 2}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_greater_than(self):
        """Test evaluating fixture with greater than operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=3,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "home_score", "operator": ">", "value": 2}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_less_than(self):
        """Test evaluating fixture with less than operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=2,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "home_score", "operator": "<", "value": 3}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_in_operator(self):
        """Test evaluating fixture with in operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "league_id", "operator": "in", "value": [1, 2, 3]}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_between_operator(self):
        """Test evaluating fixture with between operator."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=2,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "home_score", "operator": "between", "value": [1, 3]}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_multiple_conditions_all_match(self):
        """Test evaluating fixture with multiple conditions that all match."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=2,
            away_team_score=1,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [
            {"field": "home_score", "operator": ">", "value": 1},
            {"field": "away_score", "operator": "<", "value": 2},
            {"field": "league_id", "operator": "=", "value": 1},
        ]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True

    async def test_evaluate_fixture_multiple_conditions_one_fails(self):
        """Test evaluating fixture with multiple conditions where one fails."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=2,
            away_team_score=1,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [
            {"field": "home_score", "operator": ">", "value": 1},
            {"field": "away_score", "operator": ">", "value": 5},  # This will fail
        ]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is False

    async def test_evaluate_fixture_total_goals(self):
        """Test evaluating fixture with calculated total_goals field."""
        fixture = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=28,  # Finished
            home_team_id=1,
            away_team_id=2,
            home_team_score=2,
            away_team_score=1,
        )

        engine = FilterEngine(None)  # type: ignore
        rules = [{"field": "total_goals", "operator": ">", "value": 2}]

        result = engine.evaluate_fixture(fixture, rules)
        assert result is True


@pytest.mark.asyncio
class TestFilterEngineDatabase:
    """Test filter engine with database queries."""

    async def test_find_matching_fixtures(self, db: AsyncSession):
        """Test finding matching fixtures from database."""
        # Create league
        league = League(
            league_id=1,
            season_type=1,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db.add(league)
        await db.flush()

        # Create teams
        teams = [
            Team(team_id=i, name=f"Team {i}", display_name=f"Team {i}")
            for i in range(1, 7)
        ]
        db.add_all(teams)
        await db.flush()

        # Create fixtures
        fixture1 = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=3,
        )
        fixture2 = Fixture(
            id=2,
            league_id=1,
            event_id=1002,
            season_type=1,
            match_date=datetime(2024, 1, 16),
            status_id=1,
            home_team_id=3,
            away_team_id=4,
            home_team_score=1,
        )
        fixture3 = Fixture(
            id=3,
            league_id=1,
            event_id=1003,
            season_type=1,
            match_date=datetime(2024, 1, 17),
            status_id=1,
            home_team_id=5,
            away_team_id=6,
            home_team_score=4,
        )
        db.add_all([fixture1, fixture2, fixture3])
        await db.flush()

        # Find fixtures with home_score > 2
        engine = FilterEngine(db)
        rules = [{"field": "home_score", "operator": ">", "value": 2}]

        matches = await engine.find_matching_fixtures(rules)

        assert len(matches) == 2
        match_ids = [m.id for m in matches]
        assert 1 in match_ids
        assert 3 in match_ids

    async def test_find_matching_fixtures_with_date_range(self, db: AsyncSession):
        """Test finding matching fixtures with date range filter."""
        # Create league
        league = League(
            league_id=1,
            season_type=1,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db.add(league)
        await db.flush()

        # Create teams
        teams = [
            Team(team_id=i, name=f"Team {i}", display_name=f"Team {i}")
            for i in range(1, 5)
        ]
        db.add_all(teams)
        await db.flush()

        # Create fixtures
        fixture1 = Fixture(
            id=1,
            league_id=1,
            event_id=1001,
            season_type=1,
            match_date=datetime(2024, 1, 15),
            status_id=1,
            home_team_id=1,
            away_team_id=2,
            home_team_score=3,
        )
        fixture2 = Fixture(
            id=2,
            league_id=1,
            event_id=1002,
            season_type=1,
            match_date=datetime(2024, 1, 20),
            status_id=1,
            home_team_id=3,
            away_team_id=4,
            home_team_score=3,
        )
        db.add_all([fixture1, fixture2])
        await db.flush()

        # Find fixtures with date range
        engine = FilterEngine(db)
        rules = [{"field": "home_score", "operator": ">", "value": 2}]

        matches = await engine.find_matching_fixtures(
            rules, date_from=date(2024, 1, 1), date_to=date(2024, 1, 16)
        )

        assert len(matches) == 1
        assert matches[0].id == 1

    async def test_find_matching_fixtures_with_limit(self, db: AsyncSession):
        """Test finding matching fixtures with limit."""
        # Create league
        league = League(
            league_id=1,
            season_type=1,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db.add(league)
        await db.flush()

        # Create teams (need 20 teams for 10 fixtures)
        teams = [
            Team(team_id=i, name=f"Team {i}", display_name=f"Team {i}")
            for i in range(1, 21)
        ]
        db.add_all(teams)
        await db.flush()

        # Create many fixtures
        fixtures = [
            Fixture(
                id=i,
                league_id=1,
                event_id=1000 + i,
                season_type=1,
                match_date=datetime(2024, 1, 15),
                status_id=1,
                home_team_id=i,
                away_team_id=i + 10,
                home_team_score=3,
            )
            for i in range(1, 11)
        ]
        db.add_all(fixtures)
        await db.flush()

        # Find fixtures with limit
        engine = FilterEngine(db)
        rules = [{"field": "home_score", "operator": "=", "value": 3}]

        matches = await engine.find_matching_fixtures(rules, limit=5)

        assert len(matches) == 5
