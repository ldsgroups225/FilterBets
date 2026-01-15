"""Data ingestion service for loading CSV data into PostgreSQL with optimized batch processing."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from app.models import Fixture, League, Standing, Team, TeamStats, Venue


class DataIngestionService:
    """Service for ingesting CSV data into the database with optimized batch processing."""

    def __init__(
        self,
        session: AsyncSession,
        data_dir: Path | str = "data/base_data",
        batch_size: int = 500,
        max_workers: int = 3,
    ):
        """Initialize the data ingestion service.

        Args:
            session: Async database session
            data_dir: Path to directory containing CSV files
            batch_size: Number of records per batch
            max_workers: Maximum concurrent workers for parallel ingestion
        """
        self.session = session
        self.data_dir = Path(data_dir) if isinstance(data_dir, str) else data_dir
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Get engine from session for creating additional sessions
        self.engine = session.get_bind()
        self.async_session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def ingest_all(self) -> dict[str, int]:
        """Ingest all CSV files in the correct order with optimized processing.

        Returns:
            Dictionary with counts of records inserted for each entity
        """
        results = {}

        # Order matters due to foreign key constraints
        print("📥 Starting data ingestion...")
        
        print("  → Ingesting venues...")
        results["venues"] = await self.ingest_venues()
        print(f"    ✓ {results['venues']:,} venues inserted")
        
        print("  → Ingesting leagues...")
        results["leagues"] = await self.ingest_leagues()
        print(f"    ✓ {results['leagues']:,} leagues inserted")
        
        print("  → Ingesting teams...")
        results["teams"] = await self.ingest_teams()
        print(f"    ✓ {results['teams']:,} teams inserted")
        
        print("  → Ingesting fixtures...")
        results["fixtures"] = await self.ingest_fixtures()
        print(f"    ✓ {results['fixtures']:,} fixtures inserted")
        
        # Run sequentially - asyncpg doesn't support concurrent operations on same connection
        print("  → Ingesting team stats...")
        results["team_stats"] = await self.ingest_team_stats()
        print(f"    ✓ {results['team_stats']:,} team stats inserted")
        
        print("  → Ingesting standings...")
        results["standings"] = await self.ingest_standings()
        print(f"    ✓ {results['standings']:,} standings inserted")

        return results

    async def ingest_venues(self) -> int:
        """Ingest venues from venues.csv using bulk upsert.

        Returns:
            Number of venues inserted
        """
        csv_path = self.data_dir / "venues.csv"
        if not csv_path.exists():
            return 0

        # Load all venues from CSV
        venues_data = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                venues_data.append({
                    "venue_id": int(row["venueId"]),
                    "full_name": row["fullName"] if row["fullName"] != "none" else None,
                    "short_name": row["shortName"] if row["shortName"] != "none" else None,
                    "capacity": int(row["capacity"]) if row["capacity"] and row["capacity"] != "0" else None,
                    "city": row["city"] if row["city"] else None,
                    "country": row["country"] if row["country"] else None,
                })

        # Get existing venue IDs
        result = await self.session.execute(select(Venue.venue_id))
        existing_ids = {row[0] for row in result.fetchall()}

        # Filter out existing venues
        new_venues = [v for v in venues_data if v["venue_id"] not in existing_ids]
        
        if not new_venues:
            return 0

        # Bulk insert using PostgreSQL's ON CONFLICT DO NOTHING
        count = 0
        for i in range(0, len(new_venues), self.batch_size):
            batch = new_venues[i : i + self.batch_size]
            
            # Use INSERT ... ON CONFLICT DO NOTHING for idempotency
            stmt = insert(Venue).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["venue_id"])
            await self.session.execute(stmt)
            count += len(batch)

        await self.session.commit()
        return count

    async def ingest_leagues(self) -> int:
        """Ingest leagues from leagues.csv using bulk upsert.

        Returns:
            Number of leagues inserted
        """
        csv_path = self.data_dir / "leagues.csv"
        if not csv_path.exists():
            return 0

        # First pass: collect unique leagues by league_id, keeping the most recent year
        unique_leagues: dict[int, dict] = {}
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                league_id = int(row["leagueId"])
                year = int(row["year"])
                
                if league_id not in unique_leagues or year > unique_leagues[league_id]["year"]:
                    unique_leagues[league_id] = {
                        "season_type": int(row["seasonType"]),
                        "year": year,
                        "season_name": row["seasonName"],
                        "season_slug": row["seasonSlug"] if row["seasonSlug"] else None,
                        "league_id": league_id,
                        "midsize_name": row["midsizeName"] if row["midsizeName"] else None,
                        "league_name": row["leagueName"],
                        "league_short_name": row["leagueShortName"] if row["leagueShortName"] else None,
                    }

        leagues_data = list(unique_leagues.values())

        # Get existing league IDs
        result = await self.session.execute(select(League.league_id))
        existing_ids = {row[0] for row in result.fetchall()}

        # Filter out existing leagues
        new_leagues = [l for l in leagues_data if l["league_id"] not in existing_ids]
        
        if not new_leagues:
            return 0

        # Bulk insert
        count = 0
        for i in range(0, len(new_leagues), self.batch_size):
            batch = new_leagues[i : i + self.batch_size]
            
            stmt = insert(League).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["league_id"])
            await self.session.execute(stmt)
            count += len(batch)

        await self.session.commit()
        return count

    async def ingest_teams(self) -> int:
        """Ingest teams from teams.csv using bulk upsert.

        Returns:
            Number of teams inserted
        """
        csv_path = self.data_dir / "teams.csv"
        if not csv_path.exists():
            return 0

        # Pre-load valid venue_ids
        result = await self.session.execute(select(Venue.venue_id))
        valid_venue_ids = {row[0] for row in result.fetchall()}

        # Load all teams from CSV
        teams_data = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle venue_id
                venue_id_raw = row["venueId"]
                venue_id = None
                if venue_id_raw:
                    try:
                        vid = int(venue_id_raw)
                        if vid != 0 and vid in valid_venue_ids:
                            venue_id = vid
                    except (ValueError, TypeError):
                        pass

                teams_data.append({
                    "team_id": int(row["teamId"]),
                    "location": row["location"] if row["location"] else None,
                    "name": row["name"],
                    "abbreviation": row["abbreviation"] if row["abbreviation"] else None,
                    "display_name": row["displayName"],
                    "short_display_name": row["shortDisplayName"] if row["shortDisplayName"] else None,
                    "color": row["color"] if row["color"] else None,
                    "alternate_color": row["alternateColor"] if row["alternateColor"] else None,
                    "logo_url": row["logoURL"] if row["logoURL"] else None,
                    "venue_id": venue_id,
                    "slug": row["slug"] if row["slug"] else None,
                })

        # Get existing team IDs
        result = await self.session.execute(select(Team.team_id))
        existing_ids = {row[0] for row in result.fetchall()}

        # Filter out existing teams
        new_teams = [t for t in teams_data if t["team_id"] not in existing_ids]
        
        if not new_teams:
            return 0

        # Bulk insert
        count = 0
        for i in range(0, len(new_teams), self.batch_size):
            batch = new_teams[i : i + self.batch_size]
            
            stmt = insert(Team).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["team_id"])
            await self.session.execute(stmt)
            count += len(batch)

        await self.session.commit()
        return count

    async def ingest_fixtures(self) -> int:
        """Ingest fixtures from fixtures.csv using optimized batch processing.

        Returns:
            Number of fixtures inserted
        """
        csv_path = self.data_dir / "fixtures.csv"
        if not csv_path.exists():
            return 0

        # Pre-load valid IDs
        result = await self.session.execute(select(Venue.venue_id))
        valid_venue_ids = {row[0] for row in result.fetchall()}
        
        result = await self.session.execute(select(League.league_id))
        valid_league_ids = {row[0] for row in result.fetchall()}
        
        result = await self.session.execute(select(Team.team_id))
        valid_team_ids = {row[0] for row in result.fetchall()}

        # Get existing fixture IDs to avoid duplicates
        result = await self.session.execute(select(Fixture.event_id))
        existing_ids = {row[0] for row in result.fetchall()}

        # Load and validate fixtures
        fixtures_data = []
        skipped = 0
        
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                event_id = int(row["eventId"])
                
                # Skip if already exists
                if event_id in existing_ids:
                    continue

                # Validate foreign keys
                league_id = int(row["leagueId"])
                home_team_id = int(row["homeTeamId"])
                away_team_id = int(row["awayTeamId"])
                
                if (league_id not in valid_league_ids or 
                    home_team_id not in valid_team_ids or 
                    away_team_id not in valid_team_ids):
                    skipped += 1
                    continue

                # Handle venue_id
                venue_id_raw = row["venueId"]
                venue_id = None
                if venue_id_raw:
                    try:
                        vid = int(venue_id_raw)
                        if vid > 0 and vid in valid_venue_ids:
                            venue_id = vid
                    except (ValueError, TypeError):
                        pass

                fixtures_data.append({
                    "event_id": event_id,
                    "season_type": int(row["seasonType"]),
                    "league_id": league_id,
                    "match_date": datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S"),
                    "venue_id": venue_id,
                    "attendance": int(row["attendance"]) if row["attendance"] else None,
                    "home_team_id": home_team_id,
                    "away_team_id": away_team_id,
                    "home_team_winner": self._parse_bool(row["homeTeamWinner"]),
                    "away_team_winner": self._parse_bool(row["awayTeamWinner"]),
                    "home_team_score": int(row["homeTeamScore"]) if row["homeTeamScore"] else None,
                    "away_team_score": int(row["awayTeamScore"]) if row["awayTeamScore"] else None,
                    "home_team_shootout_score": int(row["homeTeamShootoutScore"]) if row["homeTeamShootoutScore"] else None,
                    "away_team_shootout_score": int(row["awayTeamShootoutScore"]) if row["awayTeamShootoutScore"] else None,
                    "status_id": int(row["statusId"]),
                    "update_time": datetime.strptime(row["updateTime"], "%Y-%m-%d %H:%M:%S") if row["updateTime"] else None,
                })

        if skipped > 0:
            print(f"    ⚠️  Skipped {skipped:,} fixtures with invalid foreign keys")

        if not fixtures_data:
            return 0

        # Bulk insert with progress tracking
        count = 0
        total = len(fixtures_data)
        
        for i in range(0, total, self.batch_size):
            batch = fixtures_data[i : i + self.batch_size]
            
            stmt = insert(Fixture).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["event_id"])
            await self.session.execute(stmt)
            
            count += len(batch)
            if total > 10000:  # Only show progress for large datasets
                print(f"      Progress: {min(i + self.batch_size, total):,}/{total:,} ({min(i + self.batch_size, total)/total*100:.1f}%)")

        await self.session.commit()
        return count

    async def ingest_team_stats(self) -> int:
        """Ingest team stats from teamStats.csv using bulk upsert.

        Returns:
            Number of team stats records inserted
        """
        csv_path = self.data_dir / "teamStats.csv"
        if not csv_path.exists():
            return 0

        # Get existing stats to avoid duplicates
        result = await self.session.execute(
            select(TeamStats.event_id, TeamStats.team_id)
        )
        existing_keys = {(row[0], row[1]) for row in result.fetchall()}

        # Pre-load valid event_ids from fixtures
        result = await self.session.execute(select(Fixture.event_id))
        valid_event_ids = {row[0] for row in result.fetchall()}

        # Pre-load valid team_ids from teams
        result = await self.session.execute(select(Team.team_id))
        valid_team_ids = {row[0] for row in result.fetchall()}

        # Load stats from CSV
        stats_data = []
        skipped_events = 0
        skipped_teams = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                event_id = int(row["eventId"])
                team_id = int(row["teamId"])
                
                # Skip if already exists
                if (event_id, team_id) in existing_keys:
                    continue

                # Skip if event_id is not in fixtures
                if event_id not in valid_event_ids:
                    skipped_events += 1
                    continue

                # Skip if team_id is not in teams
                if team_id not in valid_team_ids:
                    skipped_teams += 1
                    continue

                stats_data.append({
                    "season_type": int(row["seasonType"]),
                    "event_id": event_id,
                    "team_id": team_id,
                    "team_order": int(row["teamOrder"]),
                    "possession_pct": float(row["possessionPct"]) if row["possessionPct"] else None,
                    "fouls_committed": int(float(row["foulsCommitted"])) if row["foulsCommitted"] else None,
                    "yellow_cards": int(float(row["yellowCards"])) if row["yellowCards"] else None,
                    "red_cards": int(float(row["redCards"])) if row["redCards"] else None,
                    "offsides": int(float(row["offsides"])) if row["offsides"] else None,
                    "won_corners": int(float(row["wonCorners"])) if row["wonCorners"] else None,
                    "saves": int(float(row["saves"])) if row["saves"] else None,
                    "total_shots": int(float(row["totalShots"])) if row["totalShots"] else None,
                    "shots_on_target": int(float(row["shotsOnTarget"])) if row["shotsOnTarget"] else None,
                    "shot_pct": float(row["shotPct"]) if row["shotPct"] else None,
                    "penalty_kick_goals": int(float(row["penaltyKickGoals"])) if row["penaltyKickGoals"] else None,
                    "penalty_kick_shots": int(float(row["penaltyKickShots"])) if row["penaltyKickShots"] else None,
                    "accurate_passes": int(float(row["accuratePasses"])) if row["accuratePasses"] else None,
                    "total_passes": int(float(row["totalPasses"])) if row["totalPasses"] else None,
                    "pass_pct": float(row["passPct"]) if row["passPct"] else None,
                    "accurate_crosses": int(float(row["accurateCrosses"])) if row["accurateCrosses"] else None,
                    "total_crosses": int(float(row["totalCrosses"])) if row["totalCrosses"] else None,
                    "cross_pct": float(row["crossPct"]) if row["crossPct"] else None,
                    "total_long_balls": int(float(row["totalLongBalls"])) if row["totalLongBalls"] else None,
                    "accurate_long_balls": int(float(row["accurateLongBalls"])) if row["accurateLongBalls"] else None,
                    "longball_pct": float(row["longballPct"]) if row["longballPct"] else None,
                    "blocked_shots": int(float(row["blockedShots"])) if row["blockedShots"] else None,
                    "effective_tackles": int(float(row["effectiveTackles"])) if row["effectiveTackles"] else None,
                    "total_tackles": int(float(row["totalTackles"])) if row["totalTackles"] else None,
                    "tackle_pct": float(row["tacklePct"]) if row["tacklePct"] else None,
                    "interceptions": int(float(row["interceptions"])) if row["interceptions"] else None,
                    "effective_clearance": int(float(row["effectiveClearance"])) if row["effectiveClearance"] else None,
                    "total_clearance": int(float(row["totalClearance"])) if row["totalClearance"] else None,
                    "update_time": datetime.strptime(row["updateTime"], "%Y-%m-%d %H:%M:%S") if row["updateTime"] else None,
                })

        if skipped_events > 0:
            print(f"    ⚠️  Skipped {skipped_events:,} team stats with invalid event_ids")

        if skipped_events > 0:
            print(f"    ⚠️  Skipped {skipped_events:,} team stats with invalid event_ids")

        if skipped_teams > 0:
            print(f"    ⚠️  Skipped {skipped_teams:,} team stats with invalid team_ids")

        if not stats_data:
            return 0

        # Bulk insert
        count = 0
        total = len(stats_data)
        
        for i in range(0, total, self.batch_size):
            batch = stats_data[i : i + self.batch_size]
            
            # Use composite unique constraint
            stmt = insert(TeamStats).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["event_id", "team_id"])
            await self.session.execute(stmt)
            
            count += len(batch)
            if total > 10000:
                print(f"      Team stats progress: {min(i + self.batch_size, total):,}/{total:,} ({min(i + self.batch_size, total)/total*100:.1f}%)")

        await self.session.commit()
        return count

    async def ingest_standings(self) -> int:
        """Ingest standings from standings.csv using bulk upsert.

        Returns:
            Number of standings records inserted
        """
        csv_path = self.data_dir / "standings.csv"
        if not csv_path.exists():
            return 0

        # Get existing standings to avoid duplicates
        result = await self.session.execute(
            select(Standing.season_type, Standing.league_id, Standing.team_id)
        )
        existing_keys = {(row[0], row[1], row[2]) for row in result.fetchall()}

        # Load standings from CSV
        standings_data = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                season_type = int(row["seasonType"])
                league_id = int(row["leagueId"])
                team_id = int(row["teamId"])
                
                # Skip if already exists
                if (season_type, league_id, team_id) in existing_keys:
                    continue

                standings_data.append({
                    "season_type": season_type,
                    "year": int(row["year"]),
                    "league_id": league_id,
                    "last_match_datetime": datetime.strptime(row["last_matchDateTime"], "%Y-%m-%d %H:%M:%S") if row["last_matchDateTime"] else None,
                    "team_rank": int(row["teamRank"]) if row["teamRank"] else 0,
                    "team_id": team_id,
                    "games_played": int(row["gamesPlayed"]) if row["gamesPlayed"] else 0,
                    "wins": int(row["wins"]) if row["wins"] else 0,
                    "ties": int(row["ties"]) if row["ties"] else 0,
                    "losses": int(row["losses"]) if row["losses"] else 0,
                    "points": int(row["points"]) if row["points"] else 0,
                    "goals_for": float(row["gf"]) if row["gf"] else None,
                    "goals_against": float(row["ga"]) if row["ga"] else None,
                    "goal_difference": int(float(row["gd"])) if row["gd"] else 0,
                    "deductions": int(row["deductions"]) if row["deductions"] else 0,
                    "clean_sheets": int(float(row["clean_sheet"])) if row["clean_sheet"] else None,
                    "form": row["form"] if row["form"] else None,
                    "next_opponent": row["next_opponent"] if row["next_opponent"] else None,
                    "next_home_away": row["next_homeAway"] if row["next_homeAway"] else None,
                    "next_match_datetime": datetime.strptime(row["next_matchDateTime"], "%Y-%m-%d %H:%M:%S") if row["next_matchDateTime"] else None,
                    "timestamp": datetime.strptime(row["timeStamp"], "%Y-%m-%d %H:%M:%S") if row["timeStamp"] else None,
                    "created_at": datetime.utcnow(),  # Explicitly set for bulk insert
                })

        if not standings_data:
            return 0

        # Bulk insert
        count = 0
        total = len(standings_data)
        
        for i in range(0, total, self.batch_size):
            batch = standings_data[i : i + self.batch_size]
            
            stmt = insert(Standing).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["season_type", "league_id", "team_id"])
            await self.session.execute(stmt)
            
            count += len(batch)
            if total > 10000:
                print(f"      Standings progress: {min(i + self.batch_size, total):,}/{total:,} ({min(i + self.batch_size, total)/total*100:.1f}%)")

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
