#!/usr/bin/env python3
"""
Comprehensive data import script for FilterBets.

Imports all data from ./data/ directory:
- base_data/*.csv - Raw fixtures, teams, leagues, standings, venues
- processed/matches_for_postgres.csv - Processed matches with features

Usage:
    poetry run python backend/scripts/ingest_all_data.py [--dry-run]
    poetry run python backend/scripts/ingest_all_data.py --step base       # Base data only
    poetry run python backend/scripts/ingest_all_data.py --step processed  # Processed data only
"""

import argparse
import asyncio
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings

settings = get_settings()
DATABASE_URL = settings.database_url


async def clear_database(session: AsyncSession) -> None:
    """Clear all data from the database."""
    print("🗑️  Clearing existing data...")
    await session.execute(text("TRUNCATE TABLE filter_matches CASCADE"))
    await session.execute(text("TRUNCATE TABLE backtest_results CASCADE"))
    await session.execute(text("TRUNCATE TABLE backtest_jobs CASCADE"))
    await session.execute(text("TRUNCATE TABLE fixtures CASCADE"))
    await session.execute(text("TRUNCATE TABLE leagues CASCADE"))
    await session.execute(text("TRUNCATE TABLE teams CASCADE"))
    await session.execute(text("TRUNCATE TABLE venues CASCADE"))
    await session.execute(text("TRUNCATE TABLE standings CASCADE"))
    await session.execute(text("TRUNCATE TABLE users CASCADE"))
    await session.commit()
    print("   Database cleared.")


async def import_venues(session: AsyncSession, data_dir: Path) -> int:
    """Import venues from CSV."""
    venue_file = data_dir / "base_data" / "venues.csv"
    if not venue_file.exists():
        print("   ⚠️  venues.csv not found")
        return 0

    print("   Importing venues...")
    count = 0
    with open(venue_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text("""
                    INSERT INTO venues (venue_id, full_name, short_name, city, country, capacity, created_at)
                    VALUES (:venue_id, :full_name, :short_name, :city, :country, :capacity, NOW())
                    ON CONFLICT (venue_id) DO UPDATE SET full_name = EXCLUDED.full_name
                """),
                {
                    "venue_id": int(row["venueId"]),
                    "full_name": row.get("fullName", ""),
                    "short_name": row.get("shortName", ""),
                    "city": row.get("city", ""),
                    "country": row.get("country", ""),
                    "capacity": int(row["capacity"]) if row.get("capacity") else None,
                }
            )
            count += 1
    await session.commit()
    print(f"   ✅ Imported {count} venues")
    return count


async def import_teams(session: AsyncSession, data_dir: Path) -> int:
    """Import teams from CSV."""
    team_file = data_dir / "base_data" / "teams.csv"
    if not team_file.exists():
        print("   ⚠️  teams.csv not found")
        return 0

    print("   Importing teams...")
    count = 0
    with open(team_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text("""
                    INSERT INTO teams (team_id, name, location, abbreviation, display_name,
                                       short_display_name, color, alternate_color, logo_url, slug, created_at)
                    VALUES (:team_id, :name, :location, :abbreviation, :display_name,
                            :short_display_name, :color, :alternate_color, :logo_url, :slug, NOW())
                    ON CONFLICT (team_id) DO UPDATE SET name = EXCLUDED.name
                """),
                {
                    "team_id": int(row["teamId"]),
                    "name": row["name"],
                    "location": row.get("location", ""),
                    "abbreviation": row.get("abbreviation", ""),
                    "display_name": row.get("displayName", ""),
                    "short_display_name": row.get("shortDisplayName", ""),
                    "color": row.get("color", ""),
                    "alternate_color": row.get("alternateColor", ""),
                    "logo_url": row.get("logoURL", ""),
                    "slug": row.get("slug", ""),
                }
            )
            count += 1
    await session.commit()
    print(f"   ✅ Imported {count} teams")
    return count


async def import_leagues(session: AsyncSession, data_dir: Path) -> int:
    """Import leagues from CSV."""
    league_file = data_dir / "base_data" / "leagues.csv"
    if not league_file.exists():
        print("   ⚠️  leagues.csv not found")
        return 0

    print("   Importing leagues...")
    count = 0
    with open(league_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text("""
                    INSERT INTO leagues (season_type, year, season_name, season_slug,
                                         league_id, midsize_name, league_name, league_short_name, created_at)
                    VALUES (:season_type, :year, :season_name, :season_slug,
                            :league_id, :midsize_name, :league_name, :league_short_name, NOW())
                    ON CONFLICT (league_id, season_type, year) DO UPDATE
                    SET league_name = EXCLUDED.league_name
                """),
                {
                    "season_type": int(row["seasonType"]),
                    "year": int(row["year"]),
                    "season_name": row["seasonName"],
                    "season_slug": row.get("seasonSlug", ""),
                    "league_id": int(row["leagueId"]),
                    "midsize_name": row.get("midsizeName", ""),
                    "league_name": row["leagueName"],
                    "league_short_name": row.get("leagueShortName", ""),
                }
            )
            count += 1
    await session.commit()
    print(f"   ✅ Imported {count} league entries")
    return count


async def import_standings(session: AsyncSession, data_dir: Path) -> int:
    """Import standings from CSV."""
    standing_file = data_dir / "base_data" / "standings.csv"
    if not standing_file.exists():
        print("   ⚠️  standings.csv not found")
        return 0

    print("   Importing standings...")
    count = 0
    with open(standing_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text("""
                    INSERT INTO standings (season_type, year, league_id, team_rank, team_id,
                                           games_played, wins, ties, losses, points,
                                           goals_for, goals_against, goal_difference, deductions, form, created_at)
                    VALUES (:season_type, :year, :league_id, :team_rank, :team_id,
                            :games_played, :wins, :ties, :losses, :points,
                            :goals_for, :goals_against, :goal_difference, :deductions, :form, NOW())
                """),
                {
                    "season_type": int(row["seasonType"]),
                    "year": int(row["year"]),
                    "league_id": int(row["leagueId"]),
                    "team_rank": int(row["teamRank"]),
                    "team_id": int(row["teamId"]),
                    "games_played": int(row["gamesPlayed"]),
                    "wins": int(row["wins"]),
                    "ties": int(row["ties"]),
                    "losses": int(row["losses"]),
                    "points": int(row["points"]),
                    "goals_for": float(row["gf"]) if row.get("gf") else None,
                    "goals_against": float(row["ga"]) if row.get("ga") else None,
                    "goal_difference": float(row["gd"]) if row.get("gd") else None,
                    "deductions": int(row["deductions"]) if row.get("deductions") else 0,
                    "form": row.get("form", ""),
                }
            )
            count += 1
    await session.commit()
    print(f"   ✅ Imported {count} standings entries")
    return count


async def import_fixtures_base(session: AsyncSession, data_dir: Path) -> int:
    """Import base fixtures from CSV."""
    fixture_file = data_dir / "base_data" / "fixtures.csv"
    if not fixture_file.exists():
        print("   ⚠️  fixtures.csv not found")
        return 0

    print("   Importing base fixtures...")
    count = 0
    with open(fixture_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                home_score = int(row["homeTeamScore"]) if row.get("homeTeamScore") else None
                away_score = int(row["awayTeamScore"]) if row.get("awayTeamScore") else None
                total_goals = (home_score + away_score) if home_score and away_score else None
                match_date_str = row.get("date", "")
                match_date = datetime.strptime(match_date_str, "%Y-%m-%d %H:%M:%S") if match_date_str else None

                await session.execute(
                    text("""
                        INSERT INTO fixtures (
                            event_id, match_date, league_id, home_team_id, away_team_id,
                            home_team_score, away_team_score, status_id,
                            season_type, created_at
                        ) VALUES (
                            :event_id, :match_date, :league_id, :home_team_id, :away_team_id,
                            :home_team_score, :away_team_score, :status_id,
                            :season_type, NOW()
                        )
                        ON CONFLICT (event_id) DO UPDATE SET
                            home_team_score = EXCLUDED.home_team_score,
                            away_team_score = EXCLUDED.away_team_score
                    """),
                    {
                        "event_id": int(row["eventId"]),
                        "match_date": match_date,
                        "league_id": int(row["leagueId"]) if row.get("leagueId") else None,
                        "home_team_id": int(row["homeTeamId"]) if row.get("homeTeamId") else None,
                        "away_team_id": int(row["awayTeamId"]) if row.get("awayTeamId") else None,
                        "home_team_score": home_score,
                        "away_team_score": away_score,
                        "status_id": int(row.get("statusId", 28)),
                        "season_type": int(row.get("seasonType", 2024)),
                    }
                )
                count += 1
            except Exception as e:
                print(f"      Error importing fixture {row.get('eventId')}: {e}")
    await session.commit()
    print(f"   ✅ Imported {count} base fixtures")
    return count


async def import_processed_matches(session: AsyncSession, data_dir: Path) -> tuple[int, int]:
    """Import processed matches with features from CSV."""
    csv_file = data_dir / "processed" / "matches_for_postgres.csv"
    if not csv_file.exists():
        print("   ⚠️  matches_for_postgres.csv not found")
        return (0, 0)

    print("   Importing processed matches with features...")
    created = 0
    updated = 0
    batch_size = 500
    total_rows = 0
    
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            event_id = int(row["eventId"])
            
            home_score = int(row["homeTeamScore"]) if row.get("homeTeamScore") else None
            away_score = int(row["awayTeamScore"]) if row.get("awayTeamScore") else None
            total_goals = (home_score + away_score) if home_score and away_score else None
            
            features_metadata = {
                "total_goals": total_goals,
                "over_1_5": 1 if total_goals and total_goals > 1 else (0 if total_goals is not None else None),
                "over_2_5": 1 if total_goals and total_goals > 2 else (0 if total_goals is not None else None),
                "over_3_5": 1 if total_goals and total_goals > 3 else (0 if total_goals is not None else None),
                "btts": 1 if home_score and away_score and home_score > 0 and away_score > 0 else (0 if home_score and away_score else None),
                "home_clean_sheet": 1 if home_score is not None and away_score == 0 else (0 if home_score is not None else None),
                "away_clean_sheet": 1 if away_score is not None and home_score == 0 else (0 if away_score is not None else None),
                "home_possession_pct": float(row["home_possessionPct"]) if row.get("home_possessionPct") else None,
                "home_total_shots": float(row["home_totalShots"]) if row.get("home_totalShots") else None,
                "home_shots_on_target": float(row["home_shotsOnTarget"]) if row.get("home_shotsOnTarget") else None,
                "home_won_corners": float(row["home_wonCorners"]) if row.get("home_wonCorners") else None,
                "away_possession_pct": float(row["away_possessionPct"]) if row.get("away_possessionPct") else None,
                "away_total_shots": float(row["away_totalShots"]) if row.get("away_totalShots") else None,
                "away_shots_on_target": float(row["away_shotsOnTarget"]) if row.get("away_shotsOnTarget") else None,
                "away_won_corners": float(row["away_wonCorners"]) if row.get("away_wonCorners") else None,
                "home_form_wins_5": float(row["home_form_wins_5"]) if row.get("home_form_wins_5") else None,
                "home_form_draws_5": float(row["home_form_draws_5"]) if row.get("home_form_draws_5") else None,
                "home_form_losses_5": float(row["home_form_losses_5"]) if row.get("home_form_losses_5") else None,
                "home_form_points_5": float(row["home_form_points_5"]) if row.get("home_form_points_5") else None,
                "home_form_goals_scored_5": float(row["home_form_goals_scored_5"]) if row.get("home_form_goals_scored_5") else None,
                "home_form_goals_conceded_5": float(row["home_form_goals_conceded_5"]) if row.get("home_form_goals_conceded_5") else None,
                "home_form_clean_sheets_5": float(row["home_form_clean_sheets_5"]) if row.get("home_form_clean_sheets_5") else None,
                "home_form_wins_10": float(row["home_form_wins_10"]) if row.get("home_form_wins_10") else None,
                "home_form_draws_10": float(row["home_form_draws_10"]) if row.get("home_form_draws_10") else None,
                "home_form_losses_10": float(row["home_form_losses_10"]) if row.get("home_form_losses_10") else None,
                "home_form_points_10": float(row["home_form_points_10"]) if row.get("home_form_points_10") else None,
                "home_form_goals_scored_10": float(row["home_form_goals_scored_10"]) if row.get("home_form_goals_scored_10") else None,
                "home_form_goals_conceded_10": float(row["home_form_goals_conceded_10"]) if row.get("home_form_goals_conceded_10") else None,
                "home_form_clean_sheets_10": float(row["home_form_clean_sheets_10"]) if row.get("home_form_clean_sheets_10") else None,
                "away_form_wins_5": float(row["away_form_wins_5"]) if row.get("away_form_wins_5") else None,
                "away_form_draws_5": float(row["away_form_draws_5"]) if row.get("away_form_draws_5") else None,
                "away_form_losses_5": float(row["away_form_losses_5"]) if row.get("away_form_losses_5") else None,
                "away_form_points_5": float(row["away_form_points_5"]) if row.get("away_form_points_5") else None,
                "away_form_goals_scored_5": float(row["away_form_goals_scored_5"]) if row.get("away_form_goals_scored_5") else None,
                "away_form_goals_conceded_5": float(row["away_form_goals_conceded_5"]) if row.get("away_form_goals_conceded_5") else None,
                "away_form_clean_sheets_5": float(row["away_form_clean_sheets_5"]) if row.get("away_form_clean_sheets_5") else None,
                "away_form_wins_10": float(row["away_form_wins_10"]) if row.get("away_form_wins_10") else None,
                "away_form_draws_10": float(row["away_form_draws_10"]) if row.get("away_form_draws_10") else None,
                "away_form_losses_10": float(row["away_form_losses_10"]) if row.get("away_form_losses_10") else None,
                "away_form_points_10": float(row["away_form_points_10"]) if row.get("away_form_points_10") else None,
                "away_form_goals_scored_10": float(row["away_form_goals_scored_10"]) if row.get("away_form_goals_scored_10") else None,
                "away_form_goals_conceded_10": float(row["away_form_goals_conceded_10"]) if row.get("away_form_goals_conceded_10") else None,
                "away_form_clean_sheets_10": float(row["away_form_clean_sheets_10"]) if row.get("away_form_clean_sheets_10") else None,
            }
            
            batch.append({
                "event_id": event_id,
                "home_team_score": home_score,
                "away_team_score": away_score,
                "features_metadata": json.dumps(features_metadata),
            })
            
            if len(batch) >= batch_size:
                for item in batch:
                    result = await session.execute(
                        text("""
                            UPDATE fixtures SET
                                home_team_score = :home_team_score,
                                away_team_score = :away_team_score,
                                features_metadata = CAST(:features_metadata AS JSONB)
                            WHERE event_id = :event_id
                        """),
                        item
                    )
                    if result.rowcount > 0:
                        updated += 1
                    else:
                        created += 1
                
                await session.commit()
                total_rows += len(batch)
                print(f"      Processed {total_rows:,} records...")
                batch = []
        
        if batch:
            for item in batch:
                result = await session.execute(
                    text("""
                        UPDATE fixtures SET
                            home_team_score = :home_team_score,
                            away_team_score = :away_team_score,
                            features_metadata = CAST(:features_metadata AS JSONB)
                        WHERE event_id = :event_id
                    """),
                    item
                )
                if result.rowcount > 0:
                    updated += 1
                else:
                    created += 1
            
            await session.commit()
            total_rows += len(batch)
    
    print(f"   ✅ Updated {updated:,} fixtures, {created:,} new")
    return (created, updated)


async def get_db_stats(session: AsyncSession) -> dict:
    """Get database statistics."""
    stats = {}
    
    for table in ["fixtures", "teams", "leagues", "venues", "standings"]:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        stats[table] = result.scalar()
    
    result = await session.execute(
        text("SELECT COUNT(*) FROM fixtures WHERE features_metadata IS NOT NULL")
    )
    stats["fixtures_with_features"] = result.scalar()
    
    return stats


async def main():
    """Main import function."""
    parser = argparse.ArgumentParser(description="Import all data into FilterBets database")
    parser.add_argument("--dry-run", action="store_true", help="Don't commit changes")
    parser.add_argument("--step", choices=["all", "base", "processed"], default="all",
                        help="Which step to run: all (default), base (base_data only), processed (features only)")
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent.parent / "data"
    
    print("🚀 FilterBets Data Import")
    print("=" * 50)
    print(f"Data directory: {data_dir}")
    print(f"Step: {args.step}")
    if args.dry_run:
        print("⚠️  DRY RUN - No changes will be committed")
    print("=" * 50)

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            if args.step in ["all", "base"]:
                if not args.dry_run:
                    await clear_database(session)
                
                print("\n📥 Step 1: Base Data")
                print("-" * 30)
                
                v_count = await import_venues(session, data_dir)
                t_count = await import_teams(session, data_dir)
                l_count = await import_leagues(session, data_dir)
                s_count = await import_standings(session, data_dir)
                f_count = await import_fixtures_base(session, data_dir)

            if args.step in ["all", "processed"]:
                print("\n📥 Step 2: Processed Data (Features)")
                print("-" * 30)
                
                c_count, u_count = await import_processed_matches(session, data_dir)

            if not args.dry_run:
                print("\n📊 Final Database Stats:")
                print("-" * 30)
                stats = await get_db_stats(session)
                for table, count in stats.items():
                    print(f"   {table}: {count:,}")
            
            if args.dry_run:
                print("\n⚠️  DRY RUN COMPLETE - No changes made")
            else:
                print("\n✅ Import complete!")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
