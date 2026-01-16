"""Mock live data provider for real-time match simulation."""

import random
from datetime import datetime
from typing import Any


class MockLiveDataProvider:
    """Provides mock live match data for testing and development."""

    def __init__(self) -> None:
        self.matches = self._generate_mock_matches()
        self.last_update = datetime.utcnow()

    def _generate_mock_matches(self) -> list[dict[str, Any]]:
        """Generate realistic mock live match data."""

        mock_matches = [
            {
                "id": "match_001",
                "fixture_id": 1001,
                "home_team": "Manchester City",
                "away_team": "Liverpool",
                "home_score": 2,
                "away_score": 1,
                "minute": 67,
                "status": "LIVE",
                "league": "Premier League - England",
                "live_stats": {
                    "corners": {"home": 5, "away": 3, "total": 8},
                    "shots_on_target": {"home": 6, "away": 4, "total": 10},
                    "dangerous_attacks": {"home": 45, "away": 38, "total": 83},
                    "possession": {"home": 55, "away": 45, "total": 100},
                    "yellow_cards": {"home": 1, "away": 2, "total": 3},
                    "red_cards": {"home": 0, "away": 0, "total": 0},
                },
                "odds": {
                    "1X2": {"home": 1.85, "draw": 3.40, "away": 4.20},
                    "OVER_UNDER": {"2.5": {"over": 1.72, "under": 2.10}},
                    "BTTS": {"yes": 1.65, "no": 2.20},
                    "CORNERS": {"8.5": {"over": 1.95, "under": 1.85}},
                },
                "team_state": {
                    "home": "WINNING",
                    "away": "LOSING",
                    "momentum": "HOME",
                },
                "ai_predictions": {
                    "home_win_prob": 68,
                    "away_win_prob": 18,
                    "draw_prob": 14,
                    "over_2_5_prob": 72,
                    "btts_prob": 65,
                },
                "historical": {
                    "over_2_5_pct": 58,
                    "btts_yes_pct": 52,
                    "home_win_pct": 65,
                },
            },
            {
                "id": "match_002",
                "fixture_id": 1002,
                "home_team": "Barcelona",
                "away_team": "Real Madrid",
                "home_score": 1,
                "away_score": 1,
                "minute": 45,
                "status": "HALFTIME",
                "league": "La Liga - Spain",
                "live_stats": {
                    "corners": {"home": 4, "away": 6, "total": 10},
                    "shots_on_target": {"home": 3, "away": 5, "total": 8},
                    "dangerous_attacks": {"home": 32, "away": 41, "total": 73},
                    "possession": {"home": 48, "away": 52, "total": 100},
                    "yellow_cards": {"home": 2, "away": 1, "total": 3},
                    "red_cards": {"home": 0, "away": 0, "total": 0},
                },
                "odds": {
                    "1X2": {"home": 2.10, "draw": 3.20, "away": 3.80},
                    "OVER_UNDER": {"2.5": {"over": 1.88, "under": 1.92}},
                    "BTTS": {"yes": 1.58, "no": 2.35},
                    "CORNERS": {"9.5": {"over": 1.82, "under": 1.98}},
                },
                "team_state": {
                    "home": "DRAWING",
                    "away": "DRAWING",
                    "momentum": "NEUTRAL",
                },
                "ai_predictions": {
                    "home_win_prob": 42,
                    "away_win_prob": 35,
                    "draw_prob": 23,
                    "over_2_5_prob": 68,
                    "btts_prob": 71,
                },
                "historical": {
                    "over_2_5_pct": 62,
                    "btts_yes_pct": 68,
                    "home_win_pct": 48,
                },
            },
            {
                "id": "match_003",
                "fixture_id": 1003,
                "home_team": "Bayern Munich",
                "away_team": "Borussia Dortmund",
                "home_score": 3,
                "away_score": 2,
                "minute": 82,
                "status": "LIVE",
                "league": "Bundesliga - Germany",
                "live_stats": {
                    "corners": {"home": 7, "away": 4, "total": 11},
                    "shots_on_target": {"home": 8, "away": 6, "total": 14},
                    "dangerous_attacks": {"home": 52, "away": 44, "total": 96},
                    "possession": {"home": 58, "away": 42, "total": 100},
                    "yellow_cards": {"home": 2, "away": 3, "total": 5},
                    "red_cards": {"home": 0, "away": 1, "total": 1},
                },
                "odds": {
                    "1X2": {"home": 1.45, "draw": 4.80, "away": 6.20},
                    "OVER_UNDER": {"3.5": {"over": 1.92, "under": 1.88}},
                    "BTTS": {"yes": 1.42, "no": 2.85},
                    "CORNERS": {"10.5": {"over": 1.75, "under": 2.05}},
                },
                "team_state": {
                    "home": "WINNING",
                    "away": "LOSING",
                    "momentum": "HOME",
                },
                "ai_predictions": {
                    "home_win_prob": 72,
                    "away_win_prob": 15,
                    "draw_prob": 13,
                    "over_3_5_prob": 65,
                    "btts_prob": 78,
                },
                "historical": {
                    "over_3_5_pct": 55,
                    "btts_yes_pct": 71,
                    "home_win_pct": 68,
                },
            },
            {
                "id": "match_004",
                "fixture_id": 1004,
                "home_team": "Paris Saint-Germain",
                "away_team": "Marseille",
                "home_score": 0,
                "away_score": 1,
                "minute": 55,
                "status": "LIVE",
                "league": "Ligue 1 - France",
                "live_stats": {
                    "corners": {"home": 3, "away": 5, "total": 8},
                    "shots_on_target": {"home": 4, "away": 7, "total": 11},
                    "dangerous_attacks": {"home": 28, "away": 46, "total": 74},
                    "possession": {"home": 52, "away": 48, "total": 100},
                    "yellow_cards": {"home": 1, "away": 2, "total": 3},
                    "red_cards": {"home": 0, "away": 0, "total": 0},
                },
                "odds": {
                    "1X2": {"home": 2.85, "draw": 3.10, "away": 2.45},
                    "OVER_UNDER": {"2.5": {"over": 2.05, "under": 1.75}},
                    "BTTS": {"yes": 1.88, "no": 1.95},
                    "CORNERS": {"8.5": {"over": 1.90, "under": 1.90}},
                },
                "team_state": {
                    "home": "LOSING",
                    "away": "WINNING",
                    "momentum": "AWAY",
                },
                "ai_predictions": {
                    "home_win_prob": 38,
                    "away_win_prob": 45,
                    "draw_prob": 17,
                    "over_2_5_prob": 58,
                    "btts_prob": 62,
                },
                "historical": {
                    "over_2_5_pct": 51,
                    "btts_yes_pct": 59,
                    "home_win_pct": 62,
                },
            },
            {
                "id": "match_005",
                "fixture_id": 1005,
                "home_team": "Juventus",
                "away_team": "Inter Milan",
                "home_score": 1,
                "away_score": 1,
                "minute": 33,
                "status": "LIVE",
                "league": "Serie A - Italy",
                "live_stats": {
                    "corners": {"home": 2, "away": 4, "total": 6},
                    "shots_on_target": {"home": 2, "away": 3, "total": 5},
                    "dangerous_attacks": {"home": 25, "away": 31, "total": 56},
                    "possession": {"home": 45, "away": 55, "total": 100},
                    "yellow_cards": {"home": 0, "away": 1, "total": 1},
                    "red_cards": {"home": 0, "away": 0, "total": 0},
                },
                "odds": {
                    "1X2": {"home": 2.35, "draw": 3.15, "away": 3.20},
                    "OVER_UNDER": {"2.5": {"over": 1.95, "under": 1.85}},
                    "BTTS": {"yes": 1.75, "no": 2.10},
                    "CORNERS": {"7.5": {"over": 1.88, "under": 1.92}},
                },
                "team_state": {
                    "home": "DRAWING",
                    "away": "DRAWING",
                    "momentum": "NEUTRAL",
                },
                "ai_predictions": {
                    "home_win_prob": 35,
                    "away_win_prob": 38,
                    "draw_prob": 27,
                    "over_2_5_prob": 52,
                    "btts_prob": 58,
                },
                "historical": {
                    "over_2_5_pct": 48,
                    "btts_yes_pct": 55,
                    "home_win_pct": 42,
                },
            },
            {
                "id": "match_006",
                "fixture_id": 1006,
                "home_team": "Ajax",
                "away_team": "Feyenoord",
                "home_score": 2,
                "away_score": 2,
                "minute": 71,
                "status": "LIVE",
                "league": "Eredivisie - Netherlands",
                "live_stats": {
                    "corners": {"home": 6, "away": 5, "total": 11},
                    "shots_on_target": {"home": 5, "away": 4, "total": 9},
                    "dangerous_attacks": {"home": 38, "away": 35, "total": 73},
                    "possession": {"home": 51, "away": 49, "total": 100},
                    "yellow_cards": {"home": 2, "away": 2, "total": 4},
                    "red_cards": {"home": 0, "away": 0, "total": 0},
                },
                "odds": {
                    "1X2": {"home": 2.15, "draw": 3.25, "away": 3.55},
                    "OVER_UNDER": {"3.5": {"over": 1.85, "under": 1.95}},
                    "BTTS": {"yes": 1.52, "no": 2.45},
                    "CORNERS": {"10.5": {"over": 1.78, "under": 2.02}},
                },
                "team_state": {
                    "home": "DRAWING",
                    "away": "DRAWING",
                    "momentum": "NEUTRAL",
                },
                "ai_predictions": {
                    "home_win_prob": 40,
                    "away_win_prob": 32,
                    "draw_prob": 28,
                    "over_3_5_prob": 48,
                    "btts_prob": 69,
                },
                "historical": {
                    "over_3_5_pct": 42,
                    "btts_yes_pct": 65,
                    "home_win_pct": 45,
                },
            },
        ]

        return mock_matches

    def get_live_matches(self) -> list[dict[str, Any]]:
        """Get all currently live matches."""
        return [match for match in self.matches if match["status"] in ["LIVE", "HALFTIME"]]

    def get_match_by_id(self, match_id: str) -> dict[str, Any] | None:
        """Get a specific match by ID."""
        for match in self.matches:
            if match["id"] == match_id:
                return match
        return None

    def get_match_by_fixture_id(self, fixture_id: int) -> dict[str, Any] | None:
        """Get a specific match by fixture ID."""
        for match in self.matches:
            if match["fixture_id"] == fixture_id:
                return match
        return None

    def get_match_at_minute(self, fixture_id: int, minute: int) -> dict[str, Any] | None:
        """Get snapshot of match at specific minute for history tracking."""
        match = self.get_match_by_fixture_id(fixture_id)
        if not match:
            return None

        # Create a snapshot at the requested minute
        snapshot = match.copy()

        # Adjust stats based on minute (simplified simulation)
        minute_ratio = min(minute / 90, 1.0)

        # Scale down stats proportionally
        for stat_category in ["corners", "shots_on_target", "dangerous_attacks", "yellow_cards"]:
            if stat_category in snapshot["live_stats"]:
                for team in ["home", "away", "total"]:
                    original_value = snapshot["live_stats"][stat_category][team]
                    snapshot["live_stats"][stat_category][team] = max(
                        1, int(original_value * minute_ratio * random.uniform(0.8, 1.2))
                    )

        # Adjust scores (simplified - goals are less frequent)
        if minute < 15:
            snapshot["home_score"] = 0
            snapshot["away_score"] = 0
        elif minute < 30:
            if random.random() < 0.3:
                snapshot["home_score"] = 1
                snapshot["away_score"] = 0
        elif minute < 60:
            if random.random() < 0.5:
                snapshot["home_score"] = 1
                if random.random() < 0.3:
                    snapshot["away_score"] = 1
        else:
            # Keep original scores for later minutes
            pass

        snapshot["minute"] = minute
        return snapshot

    def update_match_data(self) -> None:
        """Simulate live data updates."""
        for match in self.matches:
            if match["status"] == "LIVE":
                # Increment minute
                match["minute"] = min(match["minute"] + 1, 90)

                # Randomly update stats (small changes)
                if random.random() < 0.3:  # 30% chance of stat change
                    stat_type = random.choice(["corners", "shots_on_target", "dangerous_attacks"])
                    team = random.choice(["home", "away"])
                    match["live_stats"][stat_type][team] += 1
                    match["live_stats"][stat_type]["total"] += 1

                # Randomly update possession
                if random.random() < 0.5:  # 50% chance of possession change
                    home_poss = match["live_stats"]["possession"]["home"]
                    change = random.randint(-2, 2)
                    new_home_poss = max(35, min(65, home_poss + change))
                    match["live_stats"]["possession"]["home"] = new_home_poss
                    match["live_stats"]["possession"]["away"] = 100 - new_home_poss

                # Check for halftime
                if match["minute"] == 45:
                    match["status"] = "HALFTIME"
                elif match["minute"] == 46:
                    match["status"] = "LIVE"

                # End match
                elif match["minute"] >= 90:
                    match["status"] = "FULLTIME"

        self.last_update = datetime.utcnow()

    def get_live_odds(self, fixture_id: int) -> list[dict[str, Any]]:
        """Get live odds for a specific fixture."""
        match = self.get_match_by_fixture_id(fixture_id)
        if not match:
            return []

        odds_list = []
        odds_data = match["odds"]

        # Convert odds data to list format
        for market, selections in odds_data.items():
            if market == "1X2":
                for selection, odds in selections.items():
                    odds_list.append({
                        "fixture_id": fixture_id,
                        "market_type": market,
                        "selection": selection.upper(),
                        "line": None,
                        "odds": odds,
                        "fetched_at": datetime.utcnow(),
                    })
            elif market in ["OVER_UNDER", "CORNERS"]:
                for line, selection_data in selections.items():
                    for selection, odds in selection_data.items():
                        odds_list.append({
                            "fixture_id": fixture_id,
                            "market_type": market,
                            "selection": selection.upper(),
                            "line": float(line) if line else None,
                            "odds": odds,
                            "fetched_at": datetime.utcnow(),
                        })
            elif market == "BTTS":
                for selection, odds in selections.items():
                    odds_list.append({
                        "fixture_id": fixture_id,
                        "market_type": market,
                        "selection": selection.upper(),
                        "line": None,
                        "odds": odds,
                        "fetched_at": datetime.utcnow(),
                    })

        return odds_list
