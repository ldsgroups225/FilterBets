// Filter field definitions and options
// Aligned with backend notebooks feature engineering

export type FieldType = 'number' | 'string' | 'select' | 'multiselect'

export interface FilterFieldOption {
  field: string
  label: string
  type: FieldType
  operators: Array<'=' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'between'>
  options?: Array<{ value: string, label: string }> // For select/multiselect
  min?: number
  max?: number
  step?: number
  category?: 'context' | 'home_form' | 'away_form' | 'rolling_stats' | 'h2h' | 'legacy'
  isPrematch?: boolean // True = safe for filter conditions, False = ground truth only
}

export const FILTER_FIELDS: FilterFieldOption[] = [
  // ============================================================
  // MATCH CONTEXT
  // ============================================================
  {
    field: 'league_id',
    label: 'League',
    type: 'number',
    operators: ['=', '!=', 'in'],
    min: 1,
    max: 10000,
    step: 1,
    category: 'context',
    isPrematch: true,
  },
  {
    field: 'tier',
    label: 'League Tier',
    type: 'select',
    operators: ['=', '!=', 'in'],
    options: [
      { value: '1', label: 'Tier 1 - Top 5 European' },
      { value: '2', label: 'Tier 2 - Major Leagues' },
      { value: '3', label: 'Tier 3 - Other' },
    ],
    category: 'context',
    isPrematch: true,
  },
  {
    field: 'status_id',
    label: 'Match Status',
    type: 'select',
    operators: ['=', '!='],
    options: [
      { value: '1', label: 'Scheduled' },
      { value: '28', label: 'Full Time' },
      { value: '45', label: 'After Extra Time' },
      { value: '47', label: 'After Penalties' },
    ],
    category: 'context',
    isPrematch: true,
  },

  // ============================================================
  // HOME TEAM FORM (Last 5 Games) - PRE-MATCH
  // ============================================================
  {
    field: 'home_form_wins_5',
    label: 'Home Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_draws_5',
    label: 'Home Team Draws (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_losses_5',
    label: 'Home Team Losses (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_points_5',
    label: 'Home Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_goals_scored_5',
    label: 'Home Team Goals Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_goals_conceded_5',
    label: 'Home Team Goals Conceded Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_clean_sheets_5',
    label: 'Home Team Clean Sheets (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },

  // ============================================================
  // HOME TEAM FORM (Last 10 Games) - PRE-MATCH
  // ============================================================
  {
    field: 'home_form_wins_10',
    label: 'Home Team Wins (Last 10)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },
  {
    field: 'home_form_points_10',
    label: 'Home Team Points (Last 10)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 30,
    step: 1,
    category: 'home_form',
    isPrematch: true,
  },

  // ============================================================
  // AWAY TEAM FORM (Last 5 Games) - PRE-MATCH
  // ============================================================
  {
    field: 'away_form_wins_5',
    label: 'Away Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_draws_5',
    label: 'Away Team Draws (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_losses_5',
    label: 'Away Team Losses (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_points_5',
    label: 'Away Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_goals_scored_5',
    label: 'Away Team Goals Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_goals_conceded_5',
    label: 'Away Team Goals Conceded Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_clean_sheets_5',
    label: 'Away Team Clean Sheets (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },

  // ============================================================
  // AWAY TEAM FORM (Last 10 Games) - PRE-MATCH
  // ============================================================
  {
    field: 'away_form_wins_10',
    label: 'Away Team Wins (Last 10)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },
  {
    field: 'away_form_points_10',
    label: 'Away Team Points (Last 10)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 30,
    step: 1,
    category: 'away_form',
    isPrematch: true,
  },

  // ============================================================
  // ROLLING STATISTICS (Last 5 Games) - PRE-MATCH
  // ============================================================
  {
    field: 'home_possession_avg_5',
    label: 'Home Possession Avg % (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
    category: 'rolling_stats',
    isPrematch: true,
  },
  {
    field: 'home_shots_avg_5',
    label: 'Home Shots Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 30,
    step: 0.1,
    category: 'rolling_stats',
    isPrematch: true,
  },
  {
    field: 'home_corners_avg_5',
    label: 'Home Corners Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 0.1,
    category: 'rolling_stats',
    isPrematch: true,
  },
  {
    field: 'away_possession_avg_5',
    label: 'Away Possession Avg % (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
    category: 'rolling_stats',
    isPrematch: true,
  },
  {
    field: 'away_shots_avg_5',
    label: 'Away Shots Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 30,
    step: 0.1,
    category: 'rolling_stats',
    isPrematch: true,
  },
  {
    field: 'away_corners_avg_5',
    label: 'Away Corners Avg (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 0.1,
    category: 'rolling_stats',
    isPrematch: true,
  },

  // ============================================================
  // HEAD-TO-HEAD - PRE-MATCH
  // ============================================================
  {
    field: 'h2h_matches',
    label: 'H2H Matches (Last 2 Years)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 20,
    step: 1,
    category: 'h2h',
    isPrematch: true,
  },
  {
    field: 'h2h_home_wins',
    label: 'H2H Home Team Wins',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 20,
    step: 1,
    category: 'h2h',
    isPrematch: true,
  },
  {
    field: 'h2h_away_wins',
    label: 'H2H Away Team Wins',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 20,
    step: 1,
    category: 'h2h',
    isPrematch: true,
  },
  {
    field: 'h2h_avg_goals',
    label: 'H2H Avg Goals Per Match',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'h2h',
    isPrematch: true,
  },

  // ============================================================
  // LEGACY FIELDS (Backward Compatibility)
  // These map to the old field names for existing filters
  // ============================================================
  {
    field: 'home_team_form_wins_last5',
    label: '[Legacy] Home Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'home_team_form_points_last5',
    label: '[Legacy] Home Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'home_team_goals_avg',
    label: '[Legacy] Home Team Goals Avg',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'home_team_goals_conceded_avg',
    label: '[Legacy] Home Team Goals Conceded Avg',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'home_team_clean_sheet_pct',
    label: '[Legacy] Home Team Clean Sheet %',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'home_team_points_per_game',
    label: '[Legacy] Home Team Points Per Game',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 3,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_form_wins_last5',
    label: '[Legacy] Away Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_form_points_last5',
    label: '[Legacy] Away Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_goals_avg',
    label: '[Legacy] Away Team Goals Avg',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_goals_conceded_avg',
    label: '[Legacy] Away Team Goals Conceded Avg',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_clean_sheet_pct',
    label: '[Legacy] Away Team Clean Sheet %',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'away_team_points_per_game',
    label: '[Legacy] Away Team Points Per Game',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 3,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
  {
    field: 'total_expected_goals',
    label: '[Legacy] Total Expected Goals',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
    category: 'legacy',
    isPrematch: true,
  },
]

export const OPERATOR_LABELS: Record<string, string> = {
  '=': 'equals',
  '!=': 'not equals',
  '>': 'greater than',
  '<': 'less than',
  '>=': 'greater or equal',
  '<=': 'less or equal',
  'in': 'in',
  'between': 'between',
}

export const CATEGORY_LABELS: Record<string, string> = {
  context: 'Match Context',
  home_form: 'Home Team Form',
  away_form: 'Away Team Form',
  rolling_stats: 'Rolling Statistics',
  h2h: 'Head-to-Head',
  legacy: 'Legacy Fields',
}

export function getFieldConfig(fieldName: string): FilterFieldOption | undefined {
  return FILTER_FIELDS.find(f => f.field === fieldName)
}

export function getFieldsByCategory(category: string): FilterFieldOption[] {
  return FILTER_FIELDS.filter(f => f.category === category)
}

export function getPrematchFields(): FilterFieldOption[] {
  return FILTER_FIELDS.filter(f => f.isPrematch)
}

export function getNonLegacyFields(): FilterFieldOption[] {
  return FILTER_FIELDS.filter(f => f.category !== 'legacy')
}
