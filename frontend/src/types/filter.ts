// Filter types

import type { PaginatedResponse } from './common'

export interface FilterRule {
  field: string
  operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'between'
  value: string | number | string[] | [number, number]
}

export interface Filter {
  id: number
  user_id: number
  name: string
  description: string | null
  rules: FilterRule[]
  is_active: boolean
  alerts_enabled: boolean
  created_at: string
  updated_at: string
}

export interface CreateFilterRequest {
  name: string
  description?: string
  rules: FilterRule[]
  is_active?: boolean
}

export interface UpdateFilterRequest {
  name?: string
  description?: string
  rules?: FilterRule[]
  is_active?: boolean
  alerts_enabled?: boolean
}

export type FilterListResponse = PaginatedResponse<Filter>
