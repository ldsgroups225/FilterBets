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
  // Odds-based fields
  {
    field: 'home_odds',
    label: 'Home Win Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  {
    field: 'draw_odds',
    label: 'Draw Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  {
    field: 'away_odds',
    label: 'Away Win Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  {
    field: 'over_2_5_odds',
    label: 'Over 2.5 Goals Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  {
    field: 'under_2_5_odds',
    label: 'Under 2.5 Goals Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  {
    field: 'btts_yes_odds',
    label: 'BTTS Yes Odds',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1.01,
    max: 100,
    step: 0.01,
  },
  // Team form fields
  {
    field: 'home_team_position',
    label: 'Home Team League Position',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1,
    max: 20,
    step: 1,
  },
  {
    field: 'away_team_position',
    label: 'Away Team League Position',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 1,
    max: 20,
    step: 1,
  },
  {
    field: 'home_team_points',
    label: 'Home Team Points',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 114,
    step: 1,
  },
  {
    field: 'away_team_points',
    label: 'Away Team Points',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 114,
    step: 1,
  },
  {
    field: 'home_team_form_last_5',
    label: 'Home Team Form (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
  },
  {
    field: 'away_team_form_last_5',
    label: 'Away Team Form (Last 5)',
    type: 'number',
    operators: ['=', '!=', '>', '<', '>=', '<=', 'between'],
    min: 0,
    max: 15,
    step: 1,
  },
  // League selection
  {
    field: 'league_id',
    label: 'League',
    type: 'select',
    operators: ['=', '!=', 'in'],
    options: [
      { value: '1', label: 'Premier League' },
      { value: '2', label: 'La Liga' },
      { value: '3', label: 'Bundesliga' },
      { value: '4', label: 'Serie A' },
      { value: '5', label: 'Ligue 1' },
    ],
  },
]

export const BET_TYPES = [
  { value: 'home_win', label: 'Home Win' },
  { value: 'away_win', label: 'Away Win' },
  { value: 'draw', label: 'Draw' },
  { value: 'over_2_5', label: 'Over 2.5 Goals' },
  { value: 'under_2_5', label: 'Under 2.5 Goals' },
  { value: 'btts', label: 'Both Teams to Score' },
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
