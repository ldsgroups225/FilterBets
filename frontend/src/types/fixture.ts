// Fixture types

import type { PaginatedResponse } from './common'
import type { LeagueTier } from '@/lib/leagueTiers'

export interface Fixture {
  id: number
  match_date: string
  status_id: number
  home_team_id: number
  away_team_id: number
  home_team_name: string
  away_team_name: string
  home_score: number | null
  away_score: number | null
  league_id: number
  league_name: string
  league_code?: string
  tier?: LeagueTier
  season: string
  home_odds: number | null
  draw_odds: number | null
  away_odds: number | null
  home_team_logo?: string | null
  away_team_logo?: string | null
  league_logo?: string | null
  // Form features (PRE-MATCH)
  home_form_points_5?: number
  home_form_wins_5?: number
  away_form_points_5?: number
  away_form_wins_5?: number
}

export type FixtureListResponse = PaginatedResponse<Fixture>

export interface FixtureFilters {
  date_from?: string
  date_to?: string
  league_id?: number
  tier?: LeagueTier
  status_id?: number
  page?: number
  per_page?: number
}
