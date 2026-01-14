// Fixture types

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
  season: string
  home_odds: number | null
  draw_odds: number | null
  away_odds: number | null
}

export interface FixtureListResponse {
  items: Fixture[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface FixtureFilters {
  date_from?: string
  date_to?: string
  league_id?: number
  status_id?: number
  page?: number
  per_page?: number
}
