// Backtest types

export type BetType = 'home_win' | 'away_win' | 'draw' | 'over_2_5' | 'under_2_5'

export interface BacktestRequest {
  bet_type: BetType
  seasons: number[]
  stake: number
}

export interface BacktestResponse {
  filter_id: number
  bet_type: string
  seasons: number[]
  total_matches: number
  wins: number
  losses: number
  pushes: number
  win_rate: number
  total_profit: number
  roi_percentage: number
  avg_odds: number | null
  cached: boolean
  run_at: string
  analytics?: BacktestAnalytics
}

export interface StreakInfo {
  current_streak: number
  longest_winning_streak: number
  longest_losing_streak: number
}

export interface MonthlyBreakdown {
  month: string
  matches: number
  wins: number
  losses: number
  profit: number
  win_rate: number
}

export interface DrawdownInfo {
  max_drawdown: number
  max_drawdown_pct: number
  current_drawdown: number
  peak_balance: number
}

export interface ProfitPoint {
  match_number: number
  cumulative_profit: number
  date: string | null
}

export interface BacktestAnalytics {
  streaks: StreakInfo
  monthly_breakdown: MonthlyBreakdown[]
  drawdown: DrawdownInfo
  profit_curve: ProfitPoint[]
}
