"""Live filter engine for evaluating live match data against filter rules."""

import operator
from typing import Any


class LiveFilterEngine:
    """Engine for evaluating live filter rules against live match data."""

    def __init__(self) -> None:
        pass

    def evaluate_live_match(
        self,
        live_match: dict[str, Any],
        rules: list[dict[str, Any]]
    ) -> bool:
        """
        Evaluate if a live match matches all filter rules.

        Args:
            live_match: Live match data from mock provider
            rules: List of live filter rules

        Returns:
            True if match matches all conditions
        """
        return all(self._evaluate_rule(live_match, rule_dict) for rule_dict in rules)

    def _evaluate_rule(self, live_match: dict[str, Any], rule_dict: dict[str, Any]) -> bool:
        """Evaluate a single rule against live match data."""
        category = rule_dict.get("category")

        if category == "live_stats":
            return self._evaluate_live_stats_rule(live_match, rule_dict)
        elif category == "team_state":
            return self._evaluate_team_state_rule(live_match, rule_dict)
        elif category == "odds":
            return self._evaluate_odds_rule(live_match, rule_dict)
        elif category == "timing":
            return self._evaluate_timing_rule(live_match, rule_dict)
        elif category == "pre_match_stats":
            return self._evaluate_pre_match_stats_rule(live_match, rule_dict)
        else:
            # Unknown category, default to False
            return False

    def _evaluate_live_stats_rule(self, live_match: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Evaluate Live Stats rule (Category A)."""
        metric = rule["metric"]
        target = rule["target"]
        comparator = rule["comparator"]
        value = rule.get("value")
        compare_to = rule.get("compare_to")

        # Get the stat value based on metric and target
        stat_value = self._get_live_stat_value(live_match, metric, target)
        if stat_value is None:
            return False

        # Advanced mode: compare to another target
        if compare_to and value is None:
            compare_value = self._get_live_stat_value(live_match, metric, compare_to)
            if compare_value is None:
                return False
            return self._compare_values(stat_value, comparator, compare_value)

        # Numeric mode: compare to fixed value
        if value is not None:
            return self._compare_values(stat_value, comparator, value)

        return False

    def _evaluate_team_state_rule(self, live_match: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Evaluate Team State rule."""
        team_state = rule["team_state"]
        target = rule["target"]

        # Get team state from match data
        match_team_states = live_match.get("team_state", {})
        if not match_team_states:
            return False

        if target == "HOME":
            actual_state = match_team_states.get("home")
        elif target == "AWAY":
            actual_state = match_team_states.get("away")
        elif target == "EITHER":
            # Check if either team matches the state
            home_state = match_team_states.get("home")
            away_state = match_team_states.get("away")
            return self._evaluate_team_state_condition(team_state, home_state, away_state)
        else:
            return False

        return self._evaluate_single_team_state(team_state, actual_state)

    def _evaluate_odds_rule(self, live_match: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Evaluate Odds rule (Category C)."""
        market = rule["market"]
        selection = rule["selection"]
        comparator = rule["comparator"]
        value = rule["value"]
        line = rule.get("line")

        # Get odds from match data
        odds_data = live_match.get("odds", {})
        if not odds_data:
            return False

        # Find the specific odds value
        odds_value = self._get_odds_value(odds_data, market, selection, line)
        if odds_value is None:
            return False

        return self._compare_values(odds_value, comparator, value)

    def _evaluate_timing_rule(self, live_match: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Evaluate Timing rule (Category D)."""
        before_minute = rule.get("before_minute")
        after_minute = rule.get("after_minute")
        at_minute = rule.get("at_minute")

        current_minute = int(live_match.get("minute", 0))

        if at_minute is not None:
            return current_minute == int(at_minute)

        conditions = []
        if before_minute is not None:
            conditions.append(current_minute < int(before_minute))
        if after_minute is not None:
            conditions.append(current_minute > int(after_minute))

        return all(conditions) if conditions else False

    def _evaluate_pre_match_stats_rule(self, live_match: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Evaluate Pre-Match Stats rule (Category E)."""
        metric = rule["metric"]
        target = rule["target"]
        comparator = rule["comparator"]
        value = rule["value"]

        # Get stat value from AI predictions or historical data
        stat_value = self._get_pre_match_stat_value(live_match, metric, target)
        if stat_value is None:
            return False

        return self._compare_values(stat_value, comparator, value)

    def _get_live_stat_value(self, live_match: dict[str, Any], metric: str, target: str) -> float | None:
        """Get live stat value based on metric and target."""
        live_stats = live_match.get("live_stats", {})
        if not live_stats:
            return None

        # Map metrics to stat categories
        metric_map = {
            "goals": "goals",
            "total_goals": "goals",
            "corners": "corners",
            "total_corners": "corners",
            "shots_on_target": "shots_on_target",
            "total_shots_on_target": "shots_on_target",
            "dangerous_attacks": "dangerous_attacks",
            "total_dangerous_attacks": "dangerous_attacks",
            "possession": "possession",
            "yellow_cards": "yellow_cards",
            "total_yellow_cards": "yellow_cards",
            "red_cards": "red_cards",
            "total_red_cards": "red_cards",
        }

        stat_category = metric_map.get(metric)
        if not stat_category or stat_category not in live_stats:
            return None

        stat_data = live_stats[stat_category]

        # Handle special cases for goals (from score)
        if metric == "goals":
            if target == "HOME":
                return float(live_match.get("home_score", 0))
            elif target == "AWAY":
                return float(live_match.get("away_score", 0))
            elif target == "TOTAL" or target == "MATCH":
                return float(live_match.get("home_score", 0) + live_match.get("away_score", 0))

        # Handle team state targets
        if target in ["HOME", "AWAY"]:
            return float(stat_data.get(target.lower(), 0))
        elif target in ["EITHER", "MATCH", "TOTAL"]:
            return float(stat_data.get("total", 0))
        elif target in ["WINNING", "LOSING"]:
            # Get the winning/losing team's stat
            team_state = live_match.get("team_state", {})
            if target == "WINNING":
                if team_state.get("home") == "WINNING":
                    return float(stat_data.get("home", 0))
                elif team_state.get("away") == "WINNING":
                    return float(stat_data.get("away", 0))
            elif target == "LOSING":
                if team_state.get("home") == "LOSING":
                    return float(stat_data.get("home", 0))
                elif team_state.get("away") == "LOSING":
                    return float(stat_data.get("away", 0))
            return None

        return None

    def _get_odds_value(self, odds_data: dict[str, Any], market: str, selection: str, line: float | None) -> float | None:
        """Get odds value from odds data."""
        market_data = odds_data.get(market)
        if not market_data:
            return None

        if market == "1X2":
            val = market_data.get(selection.lower())
            return float(val) if val is not None else None
        elif market in ["OVER_UNDER", "CORNERS"]:
            if line:
                line_key = f"{line}"
                line_data = market_data.get(line_key)
                if line_data:
                    val = line_data.get(selection.lower())
                    return float(val) if val is not None else None
        elif market == "BTTS":
            val = market_data.get(selection.lower())
            return float(val) if val is not None else None

        return None

    def _get_pre_match_stat_value(self, live_match: dict[str, Any], metric: str, target: str) -> float | None:
        """Get pre-match stat value from AI predictions or historical data."""
        # AI predictions
        ai_predictions = live_match.get("ai_predictions", {})
        historical_stats = live_match.get("historical", {})

        # Map metrics to data sources
        if metric.startswith("ai_"):
            # AI predictions
            ai_metric = metric.replace("ai_", "")
            if ai_metric == "home_win_prob" and target == "HOME":
                return float(ai_predictions.get("home_win_prob", 0))
            elif ai_metric == "away_win_prob" and target == "AWAY":
                return float(ai_predictions.get("away_win_prob", 0))
            elif ai_metric == "draw_prob" and target in ["EITHER", "MATCH"]:
                return float(ai_predictions.get("draw_prob", 0))
            elif ai_metric == "over_2_5_prob" and target in ["EITHER", "MATCH"]:
                return float(ai_predictions.get("over_2_5_prob", 0))
            elif ai_metric == "btts_prob" and target in ["EITHER", "MATCH"]:
                return float(ai_predictions.get("btts_prob", 0))
        else:
            # Historical stats
            if metric == "historical_over_2_5_pct" and target in ["EITHER", "MATCH"]:
                return float(historical_stats.get("over_2_5_pct", 0))
            elif metric == "historical_btts_pct" and target in ["EITHER", "MATCH"]:
                return float(historical_stats.get("btts_yes_pct", 0))
            elif metric == "home_win_pct" and target == "HOME":
                return float(historical_stats.get("home_win_pct", 0))

        return None

    def _evaluate_team_state_condition(self, required_state: str, home_state: str | None, away_state: str | None) -> bool:
        """Evaluate team state condition for EITHER target."""
        conditions = {
            "WINNING": lambda: home_state == "WINNING" or away_state == "WINNING",
            "LOSING": lambda: home_state == "LOSING" or away_state == "LOSING",
            "DRAWING": lambda: home_state == "DRAWING" or away_state == "DRAWING",
            "NOT_WINNING": lambda: home_state != "WINNING" or away_state != "WINNING",
            "NOT_LOSING": lambda: home_state != "LOSING" or away_state != "LOSING",
        }
        return conditions.get(required_state, lambda: False)()

    def _evaluate_single_team_state(self, required_state: str, actual_state: str | None) -> bool:
        """Evaluate team state condition for single team."""
        if actual_state is None:
            return False

        conditions = {
            "WINNING": actual_state == "WINNING",
            "LOSING": actual_state == "LOSING",
            "DRAWING": actual_state == "DRAWING",
            "NOT_WINNING": actual_state != "WINNING",
            "NOT_LOSING": actual_state != "LOSING",
        }
        return conditions.get(required_state, False)

    def _compare_values(self, actual: float, comparator: str, expected: float) -> bool:
        """Compare two values using the specified comparator."""
        operators = {
            "=": operator.eq,
            "==": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
        }
        op = operators.get(comparator)
        if op:
            return bool(op(actual, expected))
        return False
