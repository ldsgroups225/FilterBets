// Filter field definitions and options

export type FieldType = 'number' | 'string' | 'select' | 'multiselect'

export interface FilterFieldOption {
  field: string
  label: string
  type: FieldType
  operators: Array<'=' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'between'>
  options?: Array<{ value: string; label: string }> // For select/multiselect
  min?: number
  max?: number
  step?: number
}

export const FILTER_FIELDS: FilterFieldOption[] = [
  // Match context
  {
    field: 'league_id',
    label: 'League',
    type: 'number',
    operators: ['=', '!=', 'in'],
    min: 1,
    max: 1000,
    step: 1,
  },
  {
    field: 'status_id',
    label: 'Match Status',
    type: 'number',
    operators: ['=', '!='],
    min: 1,
    max: 4,
    step: 1,
  },
  // Home team computed stats
  {
    field: 'home_team_form_wins_last5',
    label: 'Home Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
  },
  {
    field: 'home_team_form_points_last5',
    label: 'Home Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
  },
  {
    field: 'home_team_goals_avg',
    label: 'Home Team Goals Average',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
  },
  {
    field: 'home_team_goals_conceded_avg',
    label: 'Home Team Goals Conceded Average',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
  },
  {
    field: 'home_team_clean_sheet_pct',
    label: 'Home Team Clean Sheet %',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
  },
  {
    field: 'home_team_points_per_game',
    label: 'Home Team Points Per Game',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 3,
    step: 0.1,
  },
  // Away team computed stats
  {
    field: 'away_team_form_wins_last5',
    label: 'Away Team Wins (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 5,
    step: 1,
  },
  {
    field: 'away_team_form_points_last5',
    label: 'Away Team Points (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
  },
  {
    field: 'away_team_goals_avg',
    label: 'Away Team Goals Average',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
  },
  {
    field: 'away_team_goals_conceded_avg',
    label: 'Away Team Goals Conceded Average',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
  },
  {
    field: 'away_team_clean_sheet_pct',
    label: 'Away Team Clean Sheet %',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 100,
    step: 1,
  },
  {
    field: 'away_team_points_per_game',
    label: 'Away Team Points Per Game',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 3,
    step: 0.1,
  },
  // Computed fields
  {
    field: 'total_expected_goals',
    label: 'Total Expected Goals',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 10,
    step: 0.1,
  },
]

export const OPERATOR_LABELS: Record<string, string> = {
  '=': 'equals',
  '!=': 'not equals',
  '>': 'greater than',
  '<': 'less than',
  '>=': 'greater than or equal',
  '<=': 'less than or equal',
  in: 'in',
  between: 'between',
}

export function getFieldConfig(fieldName: string): FilterFieldOption | undefined {
  return FILTER_FIELDS.find((f) => f.field === fieldName)
}
