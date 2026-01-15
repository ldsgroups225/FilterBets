import type { CreateFilterRequest, Filter, FilterListResponse, UpdateFilterRequest } from '@/types/filter'
import { apiClient } from '@/api/client'

// Get all filters for current user
export async function getFilters(): Promise<FilterListResponse> {
  const response = await apiClient.get<FilterListResponse>('/api/v1/filters')
  return response.data
}

// Get single filter by ID
export async function getFilter(id: number): Promise<Filter> {
  const response = await apiClient.get<Filter>(`/api/v1/filters/${id}`)
  return response.data
}

// Create new filter
export async function createFilter(data: CreateFilterRequest): Promise<Filter> {
  const response = await apiClient.post<Filter>('/api/v1/filters', data)
  return response.data
}

// Update existing filter
export async function updateFilter(id: number, data: UpdateFilterRequest): Promise<Filter> {
  const response = await apiClient.put<Filter>(`/api/v1/filters/${id}`, data)
  return response.data
}

// Delete filter
export async function deleteFilter(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/filters/${id}`)
}

// Get active filters count
export async function getActiveFiltersCount(): Promise<number> {
  const response = await getFilters()
  return response.items.filter(f => f.is_active).length
}

// Toggle filter alerts
export async function toggleFilterAlerts(id: number, enabled: boolean): Promise<Filter> {
  const response = await apiClient.patch<Filter>(`/api/v1/filters/${id}/alerts`, {
    alerts_enabled: enabled,
  })
  return response.data
}
