"""Tests for team statistics calculator service."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team
from app.services.team_stats_calculator import TeamStatsCalculator


class TestTeamStatsCalculator:
    """Test team statistics calculator."""

    @pytest.fixture
    async def setup_data(self, db_session):
        """Set up test data."""
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
        team1 = Team(
            team_id=1,
            name="Team1",
            display_name="Team One",
        )
        team2 = Team(
            team_id=2,
            name="Team2",
            display_name="Team Two",
        )
        db_session.add_all([team1, team2])
        await db_session.commit()

        # Create fixtures with various results
        base_date = datetime(2024, 1, 1)
        fixtures = [
            # Team1 home wins
            Fixture(
                event_id=1,
                league_id=1,
                season_type=2024,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                home_team_score=3,
                away_team_score=1,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                league_id=1,
                season_type=2024,
                match_date=base_date + timedelta(days=7),
                home_team_id=1,
                away_team_id=2,
                home_team_score=2,
                away_team_score=0,
                status_id=3,
            ),
            # Team1 away loss
            Fixture(
                event_id=3,
                league_id=1,
                season_type=2024,
                match_date=base_date + timedelta(days=14),
                home_team_id=2,
                away_team_id=1,
                home_team_score=2,
                away_team_score=1,
                status_id=3,
            ),
            # Team1 home draw
            Fixture(
                event_id=4,
                league_id=1,
                season_type=2024,
                match_date=base_date + timedelta(days=21),
                home_team_id=1,
                away_team_id=2,
                home_team_score=1,
                away_team_score=1,
                status_id=3,
            ),
            # Team1 away win
            Fixture(
                event_id=5,
                league_id=1,
                season_type=2024,
                match_date=base_date + timedelta(days=28),
                home_team_id=2,
                away_team_id=1,
                home_team_score=0,
                away_team_score=2,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.commit()

        return {"team1": team1, "team2": team2, "fixtures": fixtures}

    async def test_calculate_team_overall_stats(self, db_session, setup_data):  # noqa: ARG002
        """Test calculating overall team statistics."""
        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_overall_stats(1, 2024)

        assert stats["matches_played"] == 5
        assert stats["wins"] == 3
        assert stats["draws"] == 1
        assert stats["losses"] == 1
        assert stats["goals_scored"] == 9  # 3+2+1+1+2
        assert stats["goals_conceded"] == 4  # 1+0+2+1+0
        assert stats["goals_scored_avg"] == Decimal("1.80")
        assert stats["goals_conceded_avg"] == Decimal("0.80")
        assert stats["clean_sheets"] == 2  # Two matches with 0 goals conceded (event 2 and 5)
        assert stats["clean_sheet_pct"] == Decimal("40.00")
        assert stats["failed_to_score"] == 0
        assert stats["failed_to_score_pct"] == Decimal("0.00")
        assert stats["points"] == 10  # 3*3 + 1*1
        assert stats["points_per_game"] == Decimal("2.00")

    async def test_calculate_team_home_stats(self, db_session, setup_data):  # noqa: ARG002
        """Test calculating home team statistics."""
        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_home_stats(1, 2024)

        assert stats["home_matches"] == 3
        assert stats["home_wins"] == 2
        assert stats["home_draws"] == 1
        assert stats["home_losses"] == 0
        assert stats["home_goals_scored_avg"] == Decimal("2.00")  # (3+2+1)/3
        assert stats["home_goals_conceded_avg"] == Decimal("0.67")  # (1+0+1)/3

    async def test_calculate_team_away_stats(self, db_session, setup_data):  # noqa: ARG002
        """Test calculating away team statistics."""
        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_away_stats(1, 2024)

        assert stats["away_matches"] == 2
        assert stats["away_wins"] == 1
        assert stats["away_draws"] == 0
        assert stats["away_losses"] == 1
        assert stats["away_goals_scored_avg"] == Decimal("1.50")  # (1+2)/2
        assert stats["away_goals_conceded_avg"] == Decimal("1.00")  # (2+0)/2

    async def test_calculate_team_form_last5(self, db_session, setup_data):  # noqa: ARG002
        """Test calculating team form for last 5 games."""
        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_form(1, 2024, 5)

        assert stats["form_last5_wins"] == 3
        assert stats["form_last5_draws"] == 1
        assert stats["form_last5_losses"] == 1
        assert stats["form_last5_points"] == 10
        assert stats["form_last5_goals_scored"] == 9
        assert stats["form_last5_goals_conceded"] == 4

    async def test_calculate_team_form_last10(self, db_session, setup_data):  # noqa: ARG002
        """Test calculating team form for last 10 games."""
        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_form(1, 2024, 10)

        # Only 5 matches exist, so should return those
        assert stats["form_last10_wins"] == 3
        assert stats["form_last10_draws"] == 1
        assert stats["form_last10_losses"] == 1
        assert stats["form_last10_points"] == 10
        # No goals fields for last10
        assert "form_last10_goals_scored" not in stats

    async def test_refresh_team_stats_creates_new(self, db_session, setup_data):  # noqa: ARG002
        """Test refreshing team stats creates new record."""
        calculator = TeamStatsCalculator(db_session)
        computed_stats = await calculator.refresh_team_stats(1, 2024)

        assert computed_stats.team_id == 1
        assert computed_stats.season_type == 2024
        assert computed_stats.matches_played == 5
        assert computed_stats.wins == 3
        assert computed_stats.points == 10

    async def test_refresh_team_stats_updates_existing(self, db_session, setup_data):  # noqa: ARG002
        """Test refreshing team stats updates existing record."""
        calculator = TeamStatsCalculator(db_session)

        # Create initial stats
        initial_stats = await calculator.refresh_team_stats(1, 2024)
        initial_id = initial_stats.id
        initial_computed_at = initial_stats.computed_at

        # Add a new fixture
        new_fixture = Fixture(
            event_id=6,
            league_id=1,
            season_type=2024,
            match_date=datetime(2024, 2, 1),
            home_team_id=1,
            away_team_id=2,
            home_team_score=4,
            away_team_score=0,
            status_id=3,
        )
        db_session.add(new_fixture)
        await db_session.commit()

        # Refresh stats
        updated_stats = await calculator.refresh_team_stats(1, 2024)

        # Should update same record
        assert updated_stats.id == initial_id
        assert updated_stats.matches_played == 6
        assert updated_stats.wins == 4
        assert updated_stats.points == 13
        assert updated_stats.computed_at > initial_computed_at

    async def test_empty_stats(self, db_session):
        """Test calculating stats for team with no matches."""
        # Create team without fixtures
        league = League(
            league_id=99,
            season_type=2024,
            year=2024,
            season_name="2024",
            league_name="Empty League",
        )
        team = Team(
            team_id=99,
            name="EmptyTeam",
            display_name="Empty Team",
        )
        db_session.add_all([league, team])
        await db_session.commit()

        calculator = TeamStatsCalculator(db_session)
        stats = await calculator.calculate_team_overall_stats(99, 2024)

        assert stats["matches_played"] == 0
        assert stats["wins"] == 0
        assert stats["goals_scored_avg"] == Decimal("0.00")
        assert stats["points"] == 0

    async def test_get_computed_stats_endpoint(self, client, auth_headers, db_session, setup_data):  # noqa: ARG002
        """Test GET /teams/{id}/computed-stats endpoint."""
        # First create computed stats
        calculator = TeamStatsCalculator(db_session)
        await calculator.refresh_team_stats(1, 2024)

        response = await client.get(
            "/api/v1/teams/1/computed-stats?season_type=2024",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == 1
        assert data["season_type"] == 2024
        assert data["matches_played"] == 5
        assert data["wins"] == 3
        assert data["points"] == 10

    async def test_get_computed_stats_not_found(self, client, auth_headers):
        """Test GET /teams/{id}/computed-stats returns 404 when not found."""
        response = await client.get(
            "/api/v1/teams/999/computed-stats?season_type=2024",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
