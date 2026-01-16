// Frontend mock live data for BetMines Live Scanner

import type {
  LiveMatch,
  LiveStats,
  MatchHistorySnapshot,
} from '@/types/live-filter'

// Mock live matches data
export const MOCK_LIVE_MATCHES: LiveMatch[] = [
  {
    id: 'match_001',
    fixture_id: 1001,
    home_team: 'Manchester City',
    away_team: 'Liverpool',
    home_score: 2,
    away_score: 1,
    minute: 67,
    status: 'LIVE',
    league: 'Premier League - England',
    live_stats: {
      corners: { home: 5, away: 3, total: 8 },
      shots_on_target: { home: 6, away: 4, total: 10 },
      dangerious_attacks: { home: 45, away: 38, total: 83 },
      possession: { home: 55, away: 45, total: 100 },
      yellow_cards: { home: 1, away: 2, total: 3 },
      red_cards: { home: 0, away: 0, total: 0 },
    },
    team_state: {
      home: 'WINNING',
      away: 'LOSING',
      momentum: 'HOME',
    },
    odds: {
      '1X2': { home: 1.85, draw: 3.40, away: 4.20 },
      'OVER_UNDER': { 2.5: { over: 1.72, under: 2.10 } },
      'BTTS': { yes: 1.65, no: 2.20 },
      'CORNERS': { 8.5: { over: 1.95, under: 1.85 } },
    },
    ai_predictions: {
      home_win_prob: 68,
      away_win_prob: 18,
      draw_prob: 14,
      over_2_5_prob: 72,
      btts_prob: 65,
    },
    historical_stats: {
      over_2_5_pct: 58,
      btts_yes_pct: 52,
      home_win_pct: 65,
    },
    last_update: new Date().toISOString(),
  },
  {
    id: 'match_002',
    fixture_id: 1002,
    home_team: 'Barcelona',
    away_team: 'Real Madrid',
    home_score: 1,
    away_score: 1,
    minute: 45,
    status: 'HALFTIME',
    league: 'La Liga - Spain',
    live_stats: {
      corners: { home: 4, away: 6, total: 10 },
      shots_on_target: { home: 3, away: 5, total: 8 },
      dangerious_attacks: { home: 32, away: 41, total: 73 },
      possession: { home: 48, away: 52, total: 100 },
      yellow_cards: { home: 2, away: 1, total: 3 },
      red_cards: { home: 0, away: 0, total: 0 },
    },
    team_state: {
      home: 'DRAWING',
      away: 'DRAWING',
      momentum: 'NEUTRAL',
    },
    odds: {
      '1X2': { home: 2.10, draw: 3.20, away: 3.80 },
      'OVER_UNDER': { 2.5: { over: 1.88, under: 1.92 } },
      'BTTS': { yes: 1.58, no: 2.35 },
      'CORNERS': { 9.5: { over: 1.82, under: 1.98 } },
    },
    ai_predictions: {
      home_win_prob: 42,
      away_win_prob: 35,
      draw_prob: 23,
      over_2_5_prob: 68,
      btts_prob: 71,
    },
    historical_stats: {
      over_2_5_pct: 62,
      btts_yes_pct: 68,
      home_win_pct: 48,
    },
    last_update: new Date().toISOString(),
  },
  {
    id: 'match_003',
    fixture_id: 1003,
    home_team: 'Bayern Munich',
    away_team: 'Borussia Dortmund',
    home_score: 3,
    away_score: 2,
    minute: 82,
    status: 'LIVE',
    league: 'Bundesliga - Germany',
    live_stats: {
      corners: { home: 7, away: 4, total: 11 },
      shots_on_target: { home: 8, away: 6, total: 14 },
      dangerious_attacks: { home: 52, away: 44, total: 96 },
      possession: { home: 58, away: 42, total: 100 },
      yellow_cards: { home: 2, away: 3, total: 5 },
      red_cards: { home: 0, away: 1, total: 1 },
    },
    team_state: {
      home: 'WINNING',
      away: 'LOSING',
      momentum: 'HOME',
    },
    odds: {
      '1X2': { home: 1.45, draw: 4.80, away: 6.20 },
      'OVER_UNDER': { 3.5: { over: 1.92, under: 1.88 } },
      'BTTS': { yes: 1.42, no: 2.85 },
      'CORNERS': { 10.5: { over: 1.75, under: 2.05 } },
    },
    ai_predictions: {
      home_win_prob: 72,
      away_win_prob: 15,
      draw_prob: 13,
      over_2_5_prob: 78,
      over_3_5_prob: 65,
      btts_prob: 78,
    },
    historical_stats: {
      over_2_5_pct: 72,
      over_3_5_pct: 55,
      btts_yes_pct: 71,
      home_win_pct: 68,
    },
    last_update: new Date().toISOString(),
  },
  {
    id: 'match_004',
    fixture_id: 1004,
    home_team: 'Paris Saint-Germain',
    away_team: 'Marseille',
    home_score: 0,
    away_score: 1,
    minute: 55,
    status: 'LIVE',
    league: 'Ligue 1 - France',
    live_stats: {
      corners: { home: 3, away: 5, total: 8 },
      shots_on_target: { home: 4, away: 7, total: 11 },
      dangerious_attacks: { home: 28, away: 46, total: 74 },
      possession: { home: 52, away: 48, total: 100 },
      yellow_cards: { home: 1, away: 2, total: 3 },
      red_cards: { home: 0, away: 0, total: 0 },
    },
    team_state: {
      home: 'LOSING',
      away: 'WINNING',
      momentum: 'AWAY',
    },
    odds: {
      '1X2': { home: 2.85, draw: 3.10, away: 2.45 },
      'OVER_UNDER': { 2.5: { over: 2.05, under: 1.75 } },
      'BTTS': { yes: 1.88, no: 1.95 },
      'CORNERS': { 8.5: { over: 1.90, under: 1.90 } },
    },
    ai_predictions: {
      home_win_prob: 38,
      away_win_prob: 45,
      draw_prob: 17,
      over_2_5_prob: 58,
      btts_prob: 62,
    },
    historical_stats: {
      over_2_5_pct: 51,
      btts_yes_pct: 59,
      home_win_pct: 62,
    },
    last_update: new Date().toISOString(),
  },
  {
    id: 'match_005',
    fixture_id: 1005,
    home_team: 'Juventus',
    away_team: 'Inter Milan',
    home_score: 1,
    away_score: 1,
    minute: 33,
    status: 'LIVE',
    league: 'Serie A - Italy',
    live_stats: {
      corners: { home: 2, away: 4, total: 6 },
      shots_on_target: { home: 2, away: 3, total: 5 },
      dangerious_attacks: { home: 25, away: 31, total: 56 },
      possession: { home: 45, away: 55, total: 100 },
      yellow_cards: { home: 0, away: 1, total: 1 },
      red_cards: { home: 0, away: 0, total: 0 },
    },
    team_state: {
      home: 'DRAWING',
      away: 'DRAWING',
      momentum: 'NEUTRAL',
    },
    odds: {
      '1X2': { home: 2.35, draw: 3.15, away: 3.20 },
      'OVER_UNDER': { 2.5: { over: 1.95, under: 1.85 } },
      'BTTS': { yes: 1.75, no: 2.10 },
      'CORNERS': { 7.5: { over: 1.88, under: 1.92 } },
    },
    ai_predictions: {
      home_win_prob: 35,
      away_win_prob: 38,
      draw_prob: 27,
      over_2_5_prob: 52,
      btts_prob: 58,
    },
    historical_stats: {
      over_2_5_pct: 48,
      btts_yes_pct: 55,
      home_win_pct: 42,
    },
    last_update: new Date().toISOString(),
  },
  {
    id: 'match_006',
    fixture_id: 1006,
    home_team: 'Ajax',
    away_team: 'Feyenoord',
    home_score: 2,
    away_score: 2,
    minute: 71,
    status: 'LIVE',
    league: 'Eredivisie - Netherlands',
    live_stats: {
      corners: { home: 6, away: 5, total: 11 },
      shots_on_target: { home: 5, away: 4, total: 9 },
      dangerious_attacks: { home: 38, away: 35, total: 73 },
      possession: { home: 51, away: 49, total: 100 },
      yellow_cards: { home: 2, away: 2, total: 4 },
      red_cards: { home: 0, away: 0, total: 0 },
    },
    team_state: {
      home: 'DRAWING',
      away: 'DRAWING',
      momentum: 'NEUTRAL',
    },
    odds: {
      '1X2': { home: 2.15, draw: 3.25, away: 3.55 },
      'OVER_UNDER': { 3.5: { over: 1.85, under: 1.95 } },
      'BTTS': { yes: 1.52, no: 2.45 },
      'CORNERS': { 10.5: { over: 1.78, under: 2.02 } },
    },
    ai_predictions: {
      home_win_prob: 40,
      away_win_prob: 32,
      draw_prob: 28,
      over_2_5_prob: 62,
      over_3_5_prob: 48,
      btts_prob: 69,
    },
    historical_stats: {
      over_2_5_pct: 65,
      over_3_5_pct: 42,
      btts_yes_pct: 65,
      home_win_pct: 45,
    },
    last_update: new Date().toISOString(),
  },
]

// Mock live filter results for dual-stat comparison
export const MOCK_LIVE_FILTER_RESULTS = [
  {
    id: 1,
    filter_id: 1,
    fixture_id: 1001,
    triggered_at: '2024-01-15T15:30:00Z',
    triggered_minute: 67,
    notification_value: {
      score: '2-1',
      corners: '5-3',
      possession: '55-45',
      status: 'WINNING',
      odds: { '1X2_HOME': 1.85 },
    },
    final_value: {
      score: '3-1',
      corners: '7-4',
      possession: '52-48',
      status: 'WIN',
    },
    bet_result: 'WIN' as const,
    resolved_at: '2024-01-15T17:15:00Z',
    odds_at_trigger: { '1X2_HOME': 1.85 },
  },
  {
    id: 2,
    filter_id: 1,
    fixture_id: 1002,
    triggered_at: '2024-01-15T18:45:00Z',
    triggered_minute: 45,
    notification_value: {
      score: '1-1',
      corners: '4-6',
      possession: '48-52',
      status: 'DRAWING',
      odds: { 'OVER_UNDER_2.5_OVER': 1.88 },
    },
    final_value: {
      score: '2-2',
      corners: '8-7',
      possession: '50-50',
      status: 'DRAW',
    },
    bet_result: 'WIN' as const,
    resolved_at: '2024-01-15T20:30:00Z',
    odds_at_trigger: { 'OVER_UNDER_2.5_OVER': 1.88 },
  },
  {
    id: 3,
    filter_id: 2,
    fixture_id: 1003,
    triggered_at: '2024-01-15T16:20:00Z',
    triggered_minute: 82,
    notification_value: {
      score: '3-2',
      corners: '7-4',
      possession: '58-42',
      status: 'WINNING',
      odds: { BTTS_YES: 1.42 },
    },
    final_value: {
      score: '3-2',
      corners: '7-4',
      possession: '58-42',
      status: 'WIN',
    },
    bet_result: 'WIN' as const,
    resolved_at: '2024-01-15T18:05:00Z',
    odds_at_trigger: { BTTS_YES: 1.42 },
  },
]

// Mock live scanner stats
export const MOCK_LIVE_SCANNER_STATS = {
  active_filters: 5,
  live_matches: 6,
  alerts_today: 12,
  success_rate_24h: 68.5,
  avg_odds_today: 2.15,
}

// Helper functions for frontend mock data
export class FrontendMockLiveDataProvider {
  private static instance: FrontendMockLiveDataProvider
  private matches: LiveMatch[] = [...MOCK_LIVE_MATCHES]
  private lastUpdate: Date = new Date()

  static getInstance(): FrontendMockLiveDataProvider {
    if (!FrontendMockLiveDataProvider.instance) {
      FrontendMockLiveDataProvider.instance = new FrontendMockLiveDataProvider()
    }
    return FrontendMockLiveDataProvider.instance
  }

  getLiveMatches(): LiveMatch[] {
    return this.matches.filter(match =>
      match.status === 'LIVE' || match.status === 'HALFTIME',
    )
  }

  getMatchById(matchId: string): LiveMatch | undefined {
    return this.matches.find(match => match.id === matchId)
  }

  getMatchByFixtureId(fixtureId: number): LiveMatch | undefined {
    return this.matches.find(match => match.fixture_id === fixtureId)
  }

  getMatchAtMinute(fixtureId: number, minute: number): LiveMatch | undefined {
    const match = this.getMatchByFixtureId(fixtureId)
    if (!match)
      return undefined

    // Create a snapshot at the requested minute
    const snapshot = { ...match }

    // Adjust stats based on minute (simplified simulation)
    const minuteRatio = Math.min(minute / 90, 1.0)

    // Scale down stats proportionally
    const adjustedStats: LiveStats = {
      corners: {
        home: Math.max(1, Math.floor(match.live_stats.corners.home * minuteRatio * 0.9)),
        away: Math.max(1, Math.floor(match.live_stats.corners.away * minuteRatio * 0.9)),
        total: 0,
      },
      shots_on_target: {
        home: Math.max(1, Math.floor(match.live_stats.shots_on_target.home * minuteRatio * 0.9)),
        away: Math.max(1, Math.floor(match.live_stats.shots_on_target.away * minuteRatio * 0.9)),
        total: 0,
      },
      dangerious_attacks: {
        home: Math.max(5, Math.floor(match.live_stats.dangerious_attacks.home * minuteRatio * 0.9)),
        away: Math.max(5, Math.floor(match.live_stats.dangerious_attacks.away * minuteRatio * 0.9)),
        total: 0,
      },
      possession: {
        home: match.live_stats.possession.home,
        away: match.live_stats.possession.away,
        total: 100,
      },
      yellow_cards: {
        home: Math.max(0, Math.floor(match.live_stats.yellow_cards.home * minuteRatio * 0.8)),
        away: Math.max(0, Math.floor(match.live_stats.yellow_cards.away * minuteRatio * 0.8)),
        total: 0,
      },
      red_cards: {
        home: match.live_stats.red_cards.home,
        away: match.live_stats.red_cards.away,
        total: 0,
      },
    }

    // Calculate totals
    adjustedStats.corners.total = adjustedStats.corners.home + adjustedStats.corners.away
    adjustedStats.shots_on_target.total = adjustedStats.shots_on_target.home + adjustedStats.shots_on_target.away
    adjustedStats.dangerious_attacks.total = adjustedStats.dangerious_attacks.home + adjustedStats.dangerious_attacks.away
    adjustedStats.yellow_cards.total = adjustedStats.yellow_cards.home + adjustedStats.yellow_cards.away
    adjustedStats.red_cards.total = adjustedStats.red_cards.home + adjustedStats.red_cards.away

    // Adjust scores (simplified simulation)
    if (minute < 15) {
      snapshot.home_score = 0
      snapshot.away_score = 0
    }
    else if (minute < 30) {
      snapshot.home_score = Math.random() < 0.3 ? 1 : 0
      snapshot.away_score = 0
    }
    else if (minute < 60) {
      snapshot.home_score = Math.random() < 0.5 ? 1 : 0
      snapshot.away_score = Math.random() < 0.3 ? 1 : 0
    }
    // Keep original scores for later minutes

    snapshot.live_stats = adjustedStats
    snapshot.minute = minute

    return snapshot
  }

  getMatchHistory(fixtureId: number): MatchHistorySnapshot[] {
    const match = this.getMatchByFixtureId(fixtureId)
    if (!match)
      return []

    const historyMinutes = [15, 30, 45, 60, 75, 90]
    const history: MatchHistorySnapshot[] = []

    for (const minute of historyMinutes) {
      if (minute <= match.minute) {
        const snapshot = this.getMatchAtMinute(fixtureId, minute)
        if (snapshot) {
          history.push({
            minute,
            score: `${snapshot.home_score}-${snapshot.away_score}`,
            corners: `${snapshot.live_stats.corners.home}-${snapshot.live_stats.corners.away}`,
            possession: `${snapshot.live_stats.possession.home}-${snapshot.live_stats.possession.away}`,
          })
        }
      }
    }

    return history
  }

  updateMatchData(): void {
    // Simulate live data updates
    for (const match of this.matches) {
      if (match.status === 'LIVE') {
        // Increment minute
        match.minute = Math.min(match.minute + 1, 90)

        // Randomly update stats (small changes)
        if (Math.random() < 0.3) {
          const statType = ['corners', 'shots_on_target', 'dangerious_attacks'][Math.floor(Math.random() * 3)]
          const team = Math.random() < 0.5 ? 'home' : 'away'
          match.live_stats[statType][team] += 1
          match.live_stats[statType].total += 1
        }

        // Randomly update possession
        if (Math.random() < 0.5) {
          const homePoss = match.live_stats.possession.home
          const change = Math.floor(Math.random() * 5) - 2
          const newHomePoss = Math.max(35, Math.min(65, homePoss + change))
          match.live_stats.possession.home = newHomePoss
          match.live_stats.possession.away = 100 - newHomePoss
        }

        // Check for halftime
        if (match.minute === 45) {
          match.status = 'HALFTIME'
        }
        else if (match.minute === 46) {
          match.status = 'LIVE'
        }

        // End match
        if (match.minute >= 90) {
          match.status = 'FULLTIME'
        }
      }
    }

    this.lastUpdate = new Date()
  }

  getLastUpdateTime(): Date {
    return this.lastUpdate
  }
}

// Export singleton instance
export const mockLiveDataProvider = FrontendMockLiveDataProvider.getInstance()
