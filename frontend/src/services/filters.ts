import { apiClient } from '@/api/client'
import type { Filter, FilterListResponse, CreateFilterRequest, UpdateFilterRequest } from '@/types/filter'

// Get all filters for current user
export const getFilters = async (): Promise<FilterListResponse> => {
  const response = await apiClient.get<FilterListResponse>('/api/v1/filters')
  return response.data
}

// Get single filter by ID
export const getFilter = async (id: number): Promise<Filter> => {
  const response = await apiClient.get<Filter>(`/api/v1/filters/${id}`)
  return response.data
}

// Create new filter
export const createFilter = async (data: CreateFilterRequest): Promise<Filter> => {
  const response = await apiClient.post<Filter>('/api/v1/filters', data)
  return response.data
}

// Update existing filter
export const updateFilter = async (id: number, data: UpdateFilterRequest): Promise<Filter> => {
  const response = await apiClient.put<Filter>(`/api/v1/filters/${id}`, data)
  return response.data
}

// Delete filter
export const deleteFilter = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/v1/filters/${id}`)
}

// Get active filters count
export const getActiveFiltersCount = async (): Promise<number> => {
  const response = await getFilters()
  return response.items.filter(f => f.is_active).length
}

// Toggle filter alerts
export const toggleFilterAlerts = async (id: number, enabled: boolean): Promise<Filter> => {
  const response = await apiClient.patch<Filter>(`/api/v1/filters/${id}/alerts`, {
    alerts_enabled: enabled
  })
  return response.data
}
