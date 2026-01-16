#!/usr/bin/env python3
"""Import Premier League data from processed CSV to database.

This script specifically imports Premier League matches that are not yet
in the database, along with their team statistics and league information.
"""

import argparse
import asyncio
import csv
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://filterbets:filterbets@localhost:5432/filterbets"
DATA_DIR = Path(__file__).parent.parent / "data"


async def get_existing_event_ids(session: AsyncSession) -> set[int]:
    """Get all event IDs already in the database."""
    result = await session.execute(text("SELECT id FROM fixtures"))
    return {row[0] for row in result.fetchall()}


async def get_existing_league_ids(session: AsyncSession) -> set[int]:
    """Get all league IDs already in the database."""
    result = await session.execute(text("SELECT league_id FROM leagues"))
    return {row[0] for row in result.fetchall()}


async def get_existing_team_ids(session: AsyncSession) -> set[int]:
    """Get all team IDs already in the database."""
    result = await session.execute(text("SELECT id FROM teams"))
    return {row[0] for row in result.fetchall()}


async def import_leagues(session: AsyncSession, leagues_data: list[dict[str, Any]]) -> dict[int, int]:
    """Import leagues and return mapping from league_id to database ID."""
    league_map: dict[int, int] = {}
    existing = await get_existing_league_ids(session)

    for league in leagues_data:
        league_id = league["leagueId"]
        if league_id in existing and league_id in league_map:
            continue

        result = await session.execute(
            text("""
                INSERT INTO leagues (season_type, year, season_name, season_slug,
                                     league_id, midsize_name, league_name, league_short_name)
                VALUES (:season_type, :year, :season_name, :season_slug,
                        :league_id, :midsize_name, :league_name, :league_short_name)
                ON CONFLICT (league_id, season_type, year) DO UPDATE
                SET league_name = EXCLUDED.league_name
                RETURNING id
            """),
            league
        )
        db_id = result.scalar()
        league_map[league_id] = db_id
        existing.add(league_id)

    await session.commit()
    return league_map


async def import_teams(session: AsyncSession, teams_data: list[dict[str, Any]]) -> dict[int, int]:
    """Import teams and return mapping from teamId to database ID."""
    team_map: dict[int, int] = {}
    existing = await get_existing_team_ids(session)

    for team in teams_data:
        team_id = team["teamId"]
        if team_id in existing and team_id in team_map:
            continue

        result = await session.execute(
            text("""
                INSERT INTO teams (id, location, name, abbreviation, display_name,
                                   short_display_name, color, alternate_color, logo_url, slug)
                VALUES (:teamId, :location, :name, :abbreviation, :displayName,
                        :shortDisplayName, :color, :alternateColor, :logoURL, :slug)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING id
            """),
            team
        )
        db_id = result.scalar()
        team_map[team_id] = db_id
        existing.add(team_id)

    await session.commit()
    return team_map


async def import_fixtures(
    session: AsyncSession,
    fixtures_data: list[dict[str, Any]],
    league_map: dict[int, int],
    team_map: dict[int, int],
) -> int:
    """Import fixtures and return count of new records."""
    existing = await get_existing_event_ids(session)
    new_count = 0

    for fixture in fixtures_data:
        event_id = fixture["eventId"]
        if event_id in existing:
            continue

        league_id = fixture.get("leagueId")
        home_team_id = fixture.get("homeTeamId")
        away_team_id = fixture.get("awayTeamId")

        league_db_id = league_map.get(league_id) if league_id else None
        home_db_id = team_map.get(home_team_id) if home_team_id else None
        away_db_id = team_map.get(away_team_id) if away_team_id else None

        try:
            await session.execute(
                text("""
                    INSERT INTO fixtures (
                        id, match_date, league_id, home_team_id, away_team_id,
                        home_team_score, away_team_score, status_id,
                        home_team_name, away_team_name, league_name,
                        season_type, year, result, total_goals,
                        over_1_5, over_2_5, over_3_5, btts,
                        home_clean_sheet, away_clean_sheet,
                        home_possession_pct, home_total_shots, home_shots_on_target, home_won_corners,
                        away_possession_pct, away_total_shots, away_shots_on_target, away_won_corners,
                        home_form_wins_5, home_form_draws_5, home_form_losses_5, home_form_points_5,
                        home_form_goals_scored_5, home_form_goals_conceded_5, home_form_clean_sheets_5,
                        home_form_wins_10, home_form_draws_10, home_form_losses_10, home_form_points_10,
                        home_form_goals_scored_10, home_form_goals_conceded_10, home_form_clean_sheets_10,
                        away_form_wins_5, away_form_draws_5, away_form_losses_5, away_form_points_5,
                        away_form_goals_scored_5, away_form_goals_conceded_5, away_form_clean_sheets_5,
                        away_form_wins_10, away_form_draws_10, away_form_losses_10, away_form_points_10,
                        away_form_goals_scored_10, away_form_goals_conceded_10, away_form_clean_sheets_10
                    ) VALUES (
                        :eventId, :date, :league_id, :home_team_id, :away_team_id,
                        :homeTeamScore, :awayTeamScore, 28,
                        :home_team_name, :away_team_name, :league_name,
                        :season_type, :year, :result, :total_goals,
                        :over_1_5, :over_2_5, :over_3_5, :btts,
                        :home_clean_sheet, :away_clean_sheet,
                        :home_possession_pct, :home_total_shots, :home_shots_on_target, :home_won_corners,
                        :away_possession_pct, :away_total_shots, :away_shots_on_target, :away_won_corners,
                        :home_form_wins_5, :home_form_draws_5, :home_form_losses_5, :home_form_points_5,
                        :home_form_goals_scored_5, :home_form_goals_conceded_5, :home_form_clean_sheets_5,
                        :home_form_wins_10, :home_form_draws_10, :home_form_losses_10, :home_form_points_10,
                        :home_form_goals_scored_10, :home_form_goals_conceded_10, :home_form_clean_sheets_10,
                        :away_form_wins_5, :away_form_draws_5, :away_form_losses_5, :away_form_points_5,
                        :away_form_goals_scored_5, :away_form_goals_conceded_5, :away_form_clean_sheets_5,
                        :away_form_wins_10, :away_form_draws_10, :away_form_losses_10, :away_form_points_10,
                        :away_form_goals_scored_10, :away_form_goals_conceded_10, :away_form_clean_sheets_10
                    )
                """),
                {
                    "eventId": event_id,
                    "date": fixture.get("date"),
                    "league_id": league_db_id,
                    "home_team_id": home_db_id,
                    "away_team_id": away_db_id,
                    "homeTeamScore": fixture.get("homeTeamScore"),
                    "awayTeamScore": fixture.get("awayTeamScore"),
                    "home_team_name": fixture.get("home_team_name"),
                    "away_team_name": fixture.get("away_team_name"),
                    "league_name": fixture.get("league_name"),
                    "season_type": fixture.get("seasonType") or fixture.get("tier"),
                    "year": 2024,
                    "result": fixture.get("result"),
                    "total_goals": fixture.get("total_goals"),
                    "over_1_5": fixture.get("over_1_5"),
                    "over_2_5": fixture.get("over_2_5"),
                    "over_3_5": fixture.get("over_3_5"),
                    "btts": fixture.get("btts"),
                    "home_clean_sheet": fixture.get("home_clean_sheet"),
                    "away_clean_sheet": fixture.get("away_clean_sheet"),
                    "home_possession_pct": fixture.get("home_possessionPct"),
                    "home_total_shots": fixture.get("home_totalShots"),
                    "home_shots_on_target": fixture.get("home_shotsOnTarget"),
                    "home_won_corners": fixture.get("home_wonCorners"),
                    "away_possession_pct": fixture.get("away_possessionPct"),
                    "away_total_shots": fixture.get("away_totalShots"),
                    "away_shots_on_target": fixture.get("away_shotsOnTarget"),
                    "away_won_corners": fixture.get("away_wonCorners"),
                    "home_form_wins_5": fixture.get("home_form_wins_5"),
                    "home_form_draws_5": fixture.get("home_form_draws_5"),
                    "home_form_losses_5": fixture.get("home_form_losses_5"),
                    "home_form_points_5": fixture.get("home_form_points_5"),
                    "home_form_goals_scored_5": fixture.get("home_form_goals_scored_5"),
                    "home_form_goals_conceded_5": fixture.get("home_form_goals_conceded_5"),
                    "home_form_clean_sheets_5": fixture.get("home_form_clean_sheets_5"),
                    "home_form_wins_10": fixture.get("home_form_wins_10"),
                    "home_form_draws_10": fixture.get("home_form_draws_10"),
                    "home_form_losses_10": fixture.get("home_form_losses_10"),
                    "home_form_points_10": fixture.get("home_form_points_10"),
                    "home_form_goals_scored_10": fixture.get("home_form_goals_scored_10"),
                    "home_form_goals_conceded_10": fixture.get("home_form_goals_conceded_10"),
                    "home_form_clean_sheets_10": fixture.get("home_form_clean_sheets_10"),
                    "away_form_wins_5": fixture.get("away_form_wins_5"),
                    "away_form_draws_5": fixture.get("away_form_draws_5"),
                    "away_form_losses_5": fixture.get("away_form_losses_5"),
                    "away_form_points_5": fixture.get("away_form_points_5"),
                    "away_form_goals_scored_5": fixture.get("away_form_goals_scored_5"),
                    "away_form_goals_conceded_5": fixture.get("away_form_goals_conceded_5"),
                    "away_form_clean_sheets_5": fixture.get("away_form_clean_sheets_5"),
                    "away_form_wins_10": fixture.get("away_form_wins_10"),
                    "away_form_draws_10": fixture.get("away_form_draws_10"),
                    "away_form_losses_10": fixture.get("away_form_losses_10"),
                    "away_form_points_10": fixture.get("away_form_points_10"),
                    "away_form_goals_scored_10": fixture.get("away_form_goals_scored_10"),
                    "away_form_goals_conceded_10": fixture.get("away_form_goals_conceded_10"),
                    "away_form_clean_sheets_10": fixture.get("away_form_clean_sheets_10"),
                }
            )
            new_count += 1
        except Exception as e:
            print(f"Error inserting fixture {event_id}: {e}", file=sys.stderr)

    await session.commit()
    return new_count


def load_csv_data(filepath: Path) -> list[dict[str, Any]]:
    """Load data from CSV file."""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Import Premier League data to database")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Path to data directory",
    )
    parser.add_argument(
        "--leagues",
        nargs="+",
        default=["Premier League", "English Premier League"],
        help="League names to import",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without making changes",
    )
    args = parser.parse_args()

    csv_path = args.data_dir / "processed" / "matches_for_postgres.csv"
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading data from {csv_path}...")
    all_fixtures = load_csv_data(csv_path)

    pl_fixtures = [
        f for f in all_fixtures
        if any(league.lower() in f.get("league_name", "").lower() for league in args.leagues)
    ]

    print(f"Found {len(pl_fixtures)} Premier League matches in CSV")

    if not pl_fixtures:
        print("No matching leagues found in data.")
        sys.exit(0)

    leagues_data = []
    teams_data = []
    seen_leagues: set[tuple] = set()
    seen_teams: set[int] = set()

    for fixture in pl_fixtures:
        league_key = (
            fixture.get("leagueId"),
            fixture.get("seasonType") or fixture.get("tier"),
            2024,
        )
        if league_key not in seen_leagues:
            seen_leagues.add(league_key)
            leagues_data.append({
                "leagueId": fixture.get("leagueId"),
                "season_type": fixture.get("seasonType") or fixture.get("tier"),
                "year": 2024,
                "season_name": f"{fixture.get('league_name', 'Unknown')} 2024/25",
                "season_slug": f"{fixture.get('league_name', 'unknown').lower().replace(' ', '-')}-2024-25",
                "midsize_name": fixture.get("league_name", "Unknown")[:100],
                "league_name": fixture.get("league_name", "Unknown"),
                "league_short_name": fixture.get("league_name", "Unknown")[:100],
            })

        home_id = fixture.get("homeTeamId")
        away_id = fixture.get("awayTeamId")

        if home_id and int(home_id) not in seen_teams:
            seen_teams.add(int(home_id))
            teams_data.append({
                "teamId": home_id,
                "location": "",
                "name": fixture.get("home_team_name", "Unknown"),
                "abbreviation": fixture.get("home_team_name", "Unknown")[:4].upper(),
                "displayName": fixture.get("home_team_name", "Unknown"),
                "shortDisplayName": fixture.get("home_team_name", "Unknown")[:20],
                "color": "",
                "alternateColor": "",
                "logoURL": "",
                "slug": fixture.get("home_team_name", "unknown").lower().replace(" ", "-"),
            })

        if away_id and int(away_id) not in seen_teams:
            seen_teams.add(int(away_id))
            teams_data.append({
                "teamId": away_id,
                "location": "",
                "name": fixture.get("away_team_name", "Unknown"),
                "abbreviation": fixture.get("away_team_name", "Unknown")[:4].upper(),
                "displayName": fixture.get("away_team_name", "Unknown"),
                "shortDisplayName": fixture.get("away_team_name", "Unknown")[:20],
                "color": "",
                "alternateColor": "",
                "logoURL": "",
                "slug": fixture.get("away_team_name", "unknown").lower().replace(" ", "-"),
            })

    print(f"Leagues to import: {len(leagues_data)}")
    print(f"Teams to import: {len(teams_data)}")

    if args.dry_run:
        print("\nDry run complete. No changes made.")
        return

    async def run_import():
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(lambda: None)

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            print("\nImporting leagues...")
            league_map = await import_leagues(session, leagues_data)
            print(f"  Imported {len(league_map)} leagues")

            print("\nImporting teams...")
            team_map = await import_teams(session, teams_data)
            print(f"  Imported {len(team_map)} teams")

            print("\nImporting fixtures...")
            new_count = await import_fixtures(session, pl_fixtures, league_map, team_map)
            print(f"  Imported {new_count} new fixtures")

        await engine.dispose()

    asyncio.run(run_import())
    print("\nImport complete!")


if __name__ == "__main__":
    main()
