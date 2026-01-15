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



@pytest.mark.asyncio
class TestFilterEngineComputedStats:
    """Test filter engine with computed stats fields."""

    @pytest.fixture
    async def setup_stats_data(self, db_session: AsyncSession):
        """Set up test data with computed stats."""
        from decimal import Decimal

        from app.models.team_computed_stats import TeamComputedStats

        # Create league
        league = League(
            league_id=1,
            season_type=2024,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db_session.add(league)

        # Create teams
        team1 = Team(team_id=1, name="Team1", display_name="Team One")
        team2 = Team(team_id=2, name="Team2", display_name="Team Two")
        db_session.add_all([team1, team2])
        await db_session.commit()

        # Create computed stats for team1
        stats1 = TeamComputedStats(
            team_id=1,
            season_type=2024,
            matches_played=10,
            wins=6,
            draws=2,
            losses=2,
            goals_scored=20,
            goals_conceded=10,
            goals_scored_avg=Decimal("2.00"),
            goals_conceded_avg=Decimal("1.00"),
            clean_sheets=4,
            clean_sheet_pct=Decimal("40.00"),
            failed_to_score=1,
            failed_to_score_pct=Decimal("10.00"),
            points=20,
            points_per_game=Decimal("2.00"),
            home_matches=5,
            home_wins=4,
            home_draws=1,
            home_losses=0,
            home_goals_scored_avg=Decimal("2.50"),
            home_goals_conceded_avg=Decimal("0.80"),
            away_matches=5,
            away_wins=2,
            away_draws=1,
            away_losses=2,
            away_goals_scored_avg=Decimal("1.50"),
            away_goals_conceded_avg=Decimal("1.20"),
            form_last5_wins=3,
            form_last5_draws=1,
            form_last5_losses=1,
            form_last5_points=10,
            form_last5_goals_scored=8,
            form_last5_goals_conceded=5,
            form_last10_wins=6,
            form_last10_draws=2,
            form_last10_losses=2,
            form_last10_points=20,
        )

        # Create computed stats for team2
        stats2 = TeamComputedStats(
            team_id=2,
            season_type=2024,
            matches_played=10,
            wins=3,
            draws=3,
            losses=4,
            goals_scored=12,
            goals_conceded=15,
            goals_scored_avg=Decimal("1.20"),
            goals_conceded_avg=Decimal("1.50"),
            clean_sheets=2,
            clean_sheet_pct=Decimal("20.00"),
            failed_to_score=3,
            failed_to_score_pct=Decimal("30.00"),
            points=12,
            points_per_game=Decimal("1.20"),
            home_matches=5,
            home_wins=2,
            home_draws=2,
            home_losses=1,
            home_goals_scored_avg=Decimal("1.40"),
            home_goals_conceded_avg=Decimal("1.20"),
            away_matches=5,
            away_wins=1,
            away_draws=1,
            away_losses=3,
            away_goals_scored_avg=Decimal("1.00"),
            away_goals_conceded_avg=Decimal("1.80"),
            form_last5_wins=2,
            form_last5_draws=1,
            form_last5_losses=2,
            form_last5_points=7,
            form_last5_goals_scored=6,
            form_last5_goals_conceded=7,
            form_last10_wins=3,
            form_last10_draws=3,
            form_last10_losses=4,
            form_last10_points=12,
        )

        db_session.add_all([stats1, stats2])

        # Create fixture
        fixture = Fixture(
            event_id=1001,
            league_id=1,
            season_type=2024,
            match_date=datetime(2024, 3, 15),
            home_team_id=1,
            away_team_id=2,
            status_id=1,
        )
        db_session.add(fixture)
        await db_session.commit()

        return {"fixture": fixture, "team1": team1, "team2": team2}

    async def test_filter_by_home_team_form_wins_last5(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by home team form wins (last 5 games)."""
        engine = FilterEngine(db_session)

        rules = [{"field": "home_team_form_wins_last5", "operator": ">=", "value": 3}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].home_team_id == 1

    async def test_filter_by_home_team_goals_avg(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by home team goals average."""
        engine = FilterEngine(db_session)

        rules = [{"field": "home_team_goals_avg", "operator": ">", "value": 1.5}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].home_team_id == 1

    async def test_filter_by_away_team_goals_avg(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by away team goals average."""
        engine = FilterEngine(db_session)

        rules = [{"field": "away_team_goals_avg", "operator": "<", "value": 1.5}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].away_team_id == 2

    async def test_filter_by_home_team_clean_sheet_pct(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by home team clean sheet percentage."""
        engine = FilterEngine(db_session)

        rules = [{"field": "home_team_clean_sheet_pct", "operator": ">=", "value": 30}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].home_team_id == 1

    async def test_filter_by_total_expected_goals(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by total expected goals (computed field)."""
        engine = FilterEngine(db_session)

        # home_goals_scored_avg (2.50) + away_goals_scored_avg (1.00) = 3.50
        rules = [{"field": "total_expected_goals", "operator": ">", "value": 3.0}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1

    async def test_filter_by_multiple_stats_criteria(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering with multiple computed stats criteria."""
        engine = FilterEngine(db_session)

        rules = [
            {"field": "home_team_form_wins_last5", "operator": ">=", "value": 3},
            {"field": "away_team_form_wins_last5", "operator": "<=", "value": 2},
            {"field": "home_team_points_per_game", "operator": ">", "value": 1.5},
        ]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].home_team_id == 1
        assert fixtures[0].away_team_id == 2

    async def test_filter_no_stats_available(self, db_session: AsyncSession):
        """Test filtering when no computed stats are available."""
        # Create fixture without stats
        league = League(
            league_id=99,
            season_type=2025,
            year=2025,
            season_name="2025",
            league_name="New League",
        )
        team1 = Team(team_id=99, name="NewTeam1", display_name="New Team 1")
        team2 = Team(team_id=100, name="NewTeam2", display_name="New Team 2")
        db_session.add_all([league, team1, team2])

        fixture = Fixture(
            event_id=9999,
            league_id=99,
            season_type=2025,
            match_date=datetime(2025, 1, 1),
            home_team_id=99,
            away_team_id=100,
            status_id=1,
        )
        db_session.add(fixture)
        await db_session.commit()

        engine = FilterEngine(db_session)

        rules = [{"field": "home_team_goals_avg", "operator": ">", "value": 1.0}]

        fixtures = await engine.find_matching_fixtures(rules)

        # Should return no fixtures since stats don't exist
        assert len(fixtures) == 0

    async def test_filter_by_home_team_home_goals_avg(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by home team's home goals average."""
        engine = FilterEngine(db_session)

        rules = [{"field": "home_team_home_goals_avg", "operator": ">", "value": 2.0}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].home_team_id == 1

    async def test_filter_by_away_team_away_goals_avg(
        self, db_session: AsyncSession, setup_stats_data  # noqa: ARG002
    ):
        """Test filtering by away team's away goals average."""
        engine = FilterEngine(db_session)

        rules = [{"field": "away_team_away_goals_avg", "operator": "<", "value": 1.5}]

        fixtures = await engine.find_matching_fixtures(rules)

        assert len(fixtures) == 1
        assert fixtures[0].away_team_id == 2
