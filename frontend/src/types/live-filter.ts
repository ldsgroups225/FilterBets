// Live filter types for BetMines Live Scanner

// Live rule types
export interface LiveStatsRule {
  category: 'live_stats'
  metric: 'goals' | 'total_goals' | 'corners' | 'total_corners'
    | 'shots_on_target' | 'total_shots_on_target' | 'dangerous_attacks'
    | 'total_dangerous_attacks' | 'possession' | 'yellow_cards'
    | 'total_yellow_cards' | 'red_cards' | 'total_red_cards'
  target: 'HOME' | 'AWAY' | 'EITHER' | 'MATCH' | 'FAVORITE' | 'FAVORITE_HOME'
    | 'FAVORITE_AWAY' | 'UNDERDOG' | 'UNDERDOG_HOME' | 'UNDERDOG_AWAY'
    | 'WINNING' | 'LOSING'
  comparator: '=' | '!=' | '>' | '<' | '>=' | '<='
  value?: number // For numeric mode
  compare_to?: string // For advanced mode (e.g., 'AWAY')
}

export interface TeamStateRule {
  category: 'team_state'
  team_state: 'WINNING' | 'LOSING' | 'DRAWING' | 'NOT_WINNING' | 'NOT_LOSING'
  target: 'HOME' | 'AWAY' | 'EITHER'
}

export interface OddsRule {
  category: 'odds'
  market: '1X2' | 'DOUBLE_CHANCE' | 'OVER_UNDER' | 'BTTS' | 'CORNERS'
    | 'HALF_TIME_1X2' | 'HALF_TIME_OVER_UNDER' | 'HALF_TIME_BTTS'
  selection: 'HOME' | 'DRAW' | 'AWAY' | 'OVER' | 'UNDER' | 'YES' | 'NO' | '1X' | '12' | 'X2'
  line?: number // For OU/Corners markets (e.g., 2.5)
  comparator: '=' | '!=' | '>' | '<' | '>=' | '<='
  value: number
}

export interface TimingRule {
  category: 'timing'
  before_minute?: number
  after_minute?: number
  at_minute?: number
}

export interface PreMatchStatsRule {
  category: 'pre_match_stats'
  metric: 'avg_goals_scored' | 'avg_goals_conceded' | 'clean_sheet_pct'
    | 'win_pct' | 'draw_pct' | 'loss_pct' | 'points_per_game'
    | 'ai_home_win_prob' | 'ai_away_win_prob' | 'ai_draw_prob'
    | 'ai_over_2_5_prob' | 'ai_btts_prob' | 'historical_over_2_5_pct'
    | 'historical_btts_pct' | 'historical_1x2_home_pct'
  target: 'HOME' | 'AWAY' | 'EITHER' | 'MATCH'
  comparator: '=' | '!=' | '>' | '<' | '>=' | '<='
  value: number
}

// Union type for all live rule types
export type LiveRule = LiveStatsRule | TeamStateRule | OddsRule | TimingRule | PreMatchStatsRule

// Live filter types
export interface LiveFilter {
  id: number
  user_id: number
  name: string
  description: string | null
  rules: LiveRule[]
  is_active: boolean
  filter_type: 'live' | 'backtest'
  created_at: string
  updated_at: string
}

export interface CreateLiveFilterRequest {
  name: string
  description?: string
  rules: LiveRule[]
  is_active?: boolean
  filter_type: 'live' | 'backtest'
}

export interface UpdateLiveFilterRequest {
  name?: string
  description?: string
  rules?: LiveRule[]
  is_active?: boolean
}

// Live match types
export interface LiveStats {
  corners: {
    home: number
    away: number
    total: number
  }
  shots_on_target: {
    home: number
    away: number
    total: number
  }
  dangerious_attacks: {
    home: number
    away: number
    total: number
  }
  possession: {
    home: number
    away: number
    total: number
  }
  yellow_cards: {
    home: number
    away: number
    total: number
  }
  red_cards: {
    home: number
    away: number
    total: number
  }
  [key: string]: {
    home: number
    away: number
    total: number
  } // Index signature for dynamic access
}

export interface TeamState {
  home: 'WINNING' | 'LOSING' | 'DRAWING' | 'NOT_WINNING' | 'NOT_LOSING'
  away: 'WINNING' | 'LOSING' | 'DRAWING' | 'NOT_WINNING' | 'NOT_LOSING'
  momentum: 'HOME' | 'AWAY' | 'NEUTRAL'
}

export interface AIPredictions {
  home_win_prob: number
  away_win_prob: number
  draw_prob: number
  over_2_5_prob: number
  over_3_5_prob?: number
  btts_prob: number
}

export interface HistoricalStats {
  over_2_5_pct: number
  over_3_5_pct?: number
  btts_yes_pct: number
  home_win_pct: number
}

export interface LiveMatch {
  id: string
  fixture_id: number
  home_team: string
  away_team: string
  home_score: number
  away_score: number
  minute: number
  status: 'LIVE' | 'HALFTIME' | 'FULLTIME' | 'POSTPONED' | 'CANCELLED'
  league: string
  live_stats: LiveStats
  team_state: TeamState
  odds: Record<string, any>
  ai_predictions: AIPredictions
  historical_stats: HistoricalStats
  last_update: string
}

export interface LiveOdds {
  id: number
  fixture_id: number
  market_type: string
  selection: string
  line?: number
  odds: number
  fetched_at: string
}

// Live filter result types (dual-stat comparison)
export interface LiveFilterResult {
  id: number
  filter_id: number
  fixture_id: number
  triggered_at: string
  triggered_minute: number
  notification_value: Record<string, any> // Stats at alert moment
  final_value?: Record<string, any> // Final/current stats
  bet_result: 'PENDING' | 'WIN' | 'LOSS' | 'PUSH'
  resolved_at?: string
  odds_at_trigger?: Record<string, any>
}

// Live scanner stats
export interface LiveScannerStats {
  active_filters: number
  live_matches: number
  alerts_today: number
  success_rate_24h?: number
  avg_odds_today?: number
}

// Live filter backtest types
export interface LiveFilterBacktestRequest {
  filter_id: number
  date_range?: [string, string]
  include_resolved?: boolean
}

export interface LiveFilterBacktestResponse {
  filter_id: number
  total_alerts: number
  resolved_alerts: number
  wins: number
  losses: number
  pushes: number
  success_rate: number
  avg_odds: number
  roi: number
  results: LiveFilterResult[]
}

// Live scanner API responses
export interface LiveScanResponse {
  scan_id: string
  matches_scanned: number
  filters_matched: number
  alerts_generated: number
  scan_duration_ms: number
  timestamp: string
}

export interface LiveFilterTestResponse {
  fixture_id: number
  filter_matches: boolean
  match_data: {
    home_team: string
    away_team: string
    score: string
    minute: number
    status: string
  }
  rule_evaluations: any[]
  timestamp: string
}

// Match history for dual-stat comparison
export interface MatchHistorySnapshot {
  minute: number
  score: string
  corners: string
  possession: string
}

export interface MatchHistoryResponse {
  fixture_id: number
  match: {
    home_team: string
    away_team: string
    current_score: string
    current_minute: number
  }
  history: MatchHistorySnapshot[]
}

// Filter evaluation helpers
export interface FilterEvaluationResult {
  rule: LiveRule
  matches: boolean
  actual_value?: number
  expected_value?: number
  error?: string
}

// KPI cards for live filter results
export interface LiveFilterKPI {
  alerts: number
  success_rate: number
  avg_odds: number
  roi: number
  period: string // '24h', '7d', '30d', 'all'
}

// Real-time updates
export interface LiveMatchUpdate {
  fixture_id: number
  updates: Partial<LiveMatch>
  timestamp: string
}

export interface LiveFilterAlert {
  filter_id: number
  fixture_id: number
  alert_type: 'NEW_MATCH' | 'STAT_UPDATE' | 'ODDS_CHANGE' | 'MATCH_END'
  message: string
  timestamp: string
}
