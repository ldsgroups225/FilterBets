"""Data ingestion service for loading CSV data into PostgreSQL."""

import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Fixture, League, Standing, Team, TeamStats, Venue


class DataIngestionService:
    """Service for ingesting CSV data into the database."""

    def __init__(self, session: AsyncSession, data_dir: Path | str = "data/base_data"):
        """Initialize the data ingestion service.

        Args:
            session: Async database session
            data_dir: Path to directory containing CSV files
        """
        self.session = session
        self.data_dir = Path(data_dir) if isinstance(data_dir, str) else data_dir

    async def ingest_all(self) -> dict[str, int]:
        """Ingest all CSV files in the correct order.

        Returns:
            Dictionary with counts of records inserted for each entity
        """
        results = {}

        # Order matters due to foreign key constraints
        results["venues"] = await self.ingest_venues()
        results["leagues"] = await self.ingest_leagues()
        results["teams"] = await self.ingest_teams()
        results["fixtures"] = await self.ingest_fixtures()
        results["team_stats"] = await self.ingest_team_stats()
        results["standings"] = await self.ingest_standings()

        return results

    async def ingest_venues(self) -> int:
        """Ingest venues from venues.csv.

        Returns:
            Number of venues inserted
        """
        csv_path = self.data_dir / "venues.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            venues = []

            for row in reader:
                # Check if venue already exists
                result = await self.session.execute(
                    select(Venue).where(Venue.venue_id == int(row["venueId"]))
                )
                if result.scalar_one_or_none():
                    continue

                venue = Venue(
                    venue_id=int(row["venueId"]),
                    full_name=row["fullName"] if row["fullName"] != "none" else None,
                    short_name=row["shortName"] if row["shortName"] != "none" else None,
                    capacity=int(row["capacity"]) if row["capacity"] and row["capacity"] != "0" else None,
                    city=row["city"] if row["city"] else None,
                    country=row["country"] if row["country"] else None,
                )
                venues.append(venue)
                count += 1

                # Batch insert every 1000 records
                if len(venues) >= 1000:
                    self.session.add_all(venues)
                    await self.session.flush()
                    venues = []

            # Insert remaining venues
            if venues:
                self.session.add_all(venues)
                await self.session.flush()

        await self.session.commit()
        return count

    async def ingest_leagues(self) -> int:
        """Ingest leagues from leagues.csv.

        Returns:
            Number of leagues inserted
        """
        csv_path = self.data_dir / "leagues.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            leagues = []

            for row in reader:
                # Check if league already exists
                result = await self.session.execute(
                    select(League).where(League.league_id == int(row["leagueId"]))
                )
                if result.scalar_one_or_none():
                    continue

                league = League(
                    season_type=int(row["seasonType"]),
                    year=int(row["year"]),
                    season_name=row["seasonName"],
                    season_slug=row["seasonSlug"] if row["seasonSlug"] else None,
                    league_id=int(row["leagueId"]),
                    midsize_name=row["midsizeName"] if row["midsizeName"] else None,
                    league_name=row["leagueName"],
                    league_short_name=row["leagueShortName"] if row["leagueShortName"] else None,
                )
                leagues.append(league)
                count += 1

                if len(leagues) >= 1000:
                    self.session.add_all(leagues)
                    await self.session.flush()
                    leagues = []

            if leagues:
                self.session.add_all(leagues)
                await self.session.flush()

        await self.session.commit()
        return count

    async def ingest_teams(self) -> int:
        """Ingest teams from teams.csv.

        Returns:
            Number of teams inserted
        """
        csv_path = self.data_dir / "teams.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            teams = []

            for row in reader:
                # Check if team already exists
                result = await self.session.execute(
                    select(Team).where(Team.team_id == int(row["teamId"]))
                )
                if result.scalar_one_or_none():
                    continue

                team = Team(
                    team_id=int(row["teamId"]),
                    location=row["location"] if row["location"] else None,
                    name=row["name"],
                    abbreviation=row["abbreviation"] if row["abbreviation"] else None,
                    display_name=row["displayName"],
                    short_display_name=row["shortDisplayName"] if row["shortDisplayName"] else None,
                    color=row["color"] if row["color"] else None,
                    alternate_color=row["alternateColor"] if row["alternateColor"] else None,
                    logo_url=row["logoURL"] if row["logoURL"] else None,
                    venue_id=int(row["venueId"]) if row["venueId"] else None,
                    slug=row["slug"] if row["slug"] else None,
                )
                teams.append(team)
                count += 1

                if len(teams) >= 1000:
                    self.session.add_all(teams)
                    await self.session.flush()
                    teams = []

            if teams:
                self.session.add_all(teams)
                await self.session.flush()

        await self.session.commit()
        return count

    async def ingest_fixtures(self) -> int:
        """Ingest fixtures from fixtures.csv.

        Returns:
            Number of fixtures inserted
        """
        csv_path = self.data_dir / "fixtures.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fixtures = []

            for row in reader:
                # Check if fixture already exists
                result = await self.session.execute(
                    select(Fixture).where(Fixture.event_id == int(row["eventId"]))
                )
                if result.scalar_one_or_none():
                    continue

                fixture = Fixture(
                    event_id=int(row["eventId"]),
                    season_type=int(row["seasonType"]),
                    league_id=int(row["leagueId"]),
                    match_date=datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S"),
                    venue_id=int(row["venueId"]) if row["venueId"] else None,
                    attendance=int(row["attendance"]) if row["attendance"] else None,
                    home_team_id=int(row["homeTeamId"]),
                    away_team_id=int(row["awayTeamId"]),
                    home_team_winner=self._parse_bool(row["homeTeamWinner"]),
                    away_team_winner=self._parse_bool(row["awayTeamWinner"]),
                    home_team_score=int(row["homeTeamScore"]) if row["homeTeamScore"] else None,
                    away_team_score=int(row["awayTeamScore"]) if row["awayTeamScore"] else None,
                    home_team_shootout_score=int(row["homeTeamShootoutScore"]) if row["homeTeamShootoutScore"] else None,
                    away_team_shootout_score=int(row["awayTeamShootoutScore"]) if row["awayTeamShootoutScore"] else None,
                    status_id=int(row["statusId"]),
                    update_time=datetime.strptime(row["updateTime"], "%Y-%m-%d %H:%M:%S") if row["updateTime"] else None,
                )
                fixtures.append(fixture)
                count += 1

                if len(fixtures) >= 1000:
                    self.session.add_all(fixtures)
                    await self.session.flush()
                    fixtures = []

            if fixtures:
                self.session.add_all(fixtures)
                await self.session.flush()

        await self.session.commit()
        return count

    async def ingest_team_stats(self) -> int:
        """Ingest team stats from teamStats.csv.

        Returns:
            Number of team stats records inserted
        """
        csv_path = self.data_dir / "teamStats.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            stats = []

            for row in reader:
                # Check if stat already exists
                result = await self.session.execute(
                    select(TeamStats).where(
                        TeamStats.event_id == int(row["eventId"]),
                        TeamStats.team_id == int(row["teamId"]),
                    )
                )
                if result.scalar_one_or_none():
                    continue

                stat = TeamStats(
                    season_type=int(row["seasonType"]),
                    event_id=int(row["eventId"]),
                    team_id=int(row["teamId"]),
                    team_order=int(row["teamOrder"]),
                    possession_pct=float(row["possessionPct"]) if row["possessionPct"] else None,
                    fouls_committed=int(float(row["foulsCommitted"])) if row["foulsCommitted"] else None,
                    yellow_cards=int(float(row["yellowCards"])) if row["yellowCards"] else None,
                    red_cards=int(float(row["redCards"])) if row["redCards"] else None,
                    offsides=int(float(row["offsides"])) if row["offsides"] else None,
                    won_corners=int(float(row["wonCorners"])) if row["wonCorners"] else None,
                    saves=int(float(row["saves"])) if row["saves"] else None,
                    total_shots=int(float(row["totalShots"])) if row["totalShots"] else None,
                    shots_on_target=int(float(row["shotsOnTarget"])) if row["shotsOnTarget"] else None,
                    shot_pct=float(row["shotPct"]) if row["shotPct"] else None,
                    penalty_kick_goals=int(float(row["penaltyKickGoals"])) if row["penaltyKickGoals"] else None,
                    penalty_kick_shots=int(float(row["penaltyKickShots"])) if row["penaltyKickShots"] else None,
                    accurate_passes=int(float(row["accuratePasses"])) if row["accuratePasses"] else None,
                    total_passes=int(float(row["totalPasses"])) if row["totalPasses"] else None,
                    pass_pct=float(row["passPct"]) if row["passPct"] else None,
                    accurate_crosses=int(float(row["accurateCrosses"])) if row["accurateCrosses"] else None,
                    total_crosses=int(float(row["totalCrosses"])) if row["totalCrosses"] else None,
                    cross_pct=float(row["crossPct"]) if row["crossPct"] else None,
                    total_long_balls=int(float(row["totalLongBalls"])) if row["totalLongBalls"] else None,
                    accurate_long_balls=int(float(row["accurateLongBalls"])) if row["accurateLongBalls"] else None,
                    longball_pct=float(row["longballPct"]) if row["longballPct"] else None,
                    blocked_shots=int(float(row["blockedShots"])) if row["blockedShots"] else None,
                    effective_tackles=int(float(row["effectiveTackles"])) if row["effectiveTackles"] else None,
                    total_tackles=int(float(row["totalTackles"])) if row["totalTackles"] else None,
                    tackle_pct=float(row["tacklePct"]) if row["tacklePct"] else None,
                    interceptions=int(float(row["interceptions"])) if row["interceptions"] else None,
                    effective_clearance=int(float(row["effectiveClearance"])) if row["effectiveClearance"] else None,
                    total_clearance=int(float(row["totalClearance"])) if row["totalClearance"] else None,
                    update_time=datetime.strptime(row["updateTime"], "%Y-%m-%d %H:%M:%S") if row["updateTime"] else None,
                )
                stats.append(stat)
                count += 1

                if len(stats) >= 1000:
                    self.session.add_all(stats)
                    await self.session.flush()
                    stats = []

            if stats:
                self.session.add_all(stats)
                await self.session.flush()

        await self.session.commit()
        return count

    async def ingest_standings(self) -> int:
        """Ingest standings from standings.csv.

        Returns:
            Number of standings records inserted
        """
        csv_path = self.data_dir / "standings.csv"
        if not csv_path.exists():
            return 0

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            standings = []

            for row in reader:
                # Check if standing already exists
                result = await self.session.execute(
                    select(Standing).where(
                        Standing.season_type == int(row["seasonType"]),
                        Standing.league_id == int(row["leagueId"]),
                        Standing.team_id == int(row["teamId"]),
                    )
                )
                if result.scalar_one_or_none():
                    continue

                standing = Standing(
                    season_type=int(row["seasonType"]),
                    year=int(row["year"]),
                    league_id=int(row["leagueId"]),
                    last_match_date_time=datetime.strptime(row["last_matchDateTime"], "%Y-%m-%d %H:%M:%S") if row["last_matchDateTime"] else None,
                    team_rank=int(row["teamRank"]) if row["teamRank"] else None,
                    team_id=int(row["teamId"]),
                    games_played=int(row["gamesPlayed"]) if row["gamesPlayed"] else None,
                    wins=int(row["wins"]) if row["wins"] else None,
                    ties=int(row["ties"]) if row["ties"] else None,
                    losses=int(row["losses"]) if row["losses"] else None,
                    points=int(row["points"]) if row["points"] else None,
                    gf=float(row["gf"]) if row["gf"] else None,
                    ga=float(row["ga"]) if row["ga"] else None,
                    gd=int(float(row["gd"])) if row["gd"] else None,
                    deductions=int(row["deductions"]) if row["deductions"] else None,
                    clean_sheet=int(float(row["clean_sheet"])) if row["clean_sheet"] else None,
                    form=row["form"] if row["form"] else None,
                    next_opponent=row["next_opponent"] if row["next_opponent"] else None,
                    next_home_away=row["next_homeAway"] if row["next_homeAway"] else None,
                    next_match_date_time=datetime.strptime(row["next_matchDateTime"], "%Y-%m-%d %H:%M:%S") if row["next_matchDateTime"] else None,
                    time_stamp=datetime.strptime(row["timeStamp"], "%Y-%m-%d %H:%M:%S") if row["timeStamp"] else None,
                )
                standings.append(standing)
                count += 1

                if len(standings) >= 1000:
                    self.session.add_all(standings)
                    await self.session.flush()
                    standings = []

            if standings:
                self.session.add_all(standings)
                await self.session.flush()

        await self.session.commit()
        return count

    @staticmethod
    def _parse_bool(value: str) -> bool | None:
        """Parse boolean value from CSV.

        Args:
            value: String value from CSV

        Returns:
            Boolean value or None
        """
        if not value or value.lower() == "none":
            return None
        return value.lower() == "true"
