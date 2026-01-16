import type { Fixture, FixtureFilters, FixtureListResponse } from '@/types/fixture'
import { apiClient } from '@/api/client'

// Get fixtures list with filters
export async function getFixtures(filters?: FixtureFilters): Promise<FixtureListResponse> {
  const params = new URLSearchParams()

  if (filters?.date_from)
    params.append('date_from', filters.date_from)
  if (filters?.date_to)
    params.append('date_to', filters.date_to)
  if (filters?.league_id)
    params.append('league_id', filters.league_id.toString())
  if (filters?.status_id)
    params.append('status_id', filters.status_id.toString())
  if (filters?.page)
    params.append('page', filters.page.toString())
  if (filters?.per_page)
    params.append('per_page', filters.per_page.toString())

  const response = await apiClient.get<FixtureListResponse>(
    `/api/v1/fixtures?${params.toString()}`,
  )
  return response.data
}

// Get today's fixtures
export async function getTodayFixtures(): Promise<FixtureListResponse> {
  const response = await apiClient.get<FixtureListResponse>('/api/v1/fixtures/today')
  return response.data
}

// Get upcoming fixtures
export async function getUpcomingFixtures(days: number = 7): Promise<FixtureListResponse> {
  const response = await apiClient.get<FixtureListResponse>(`/api/v1/fixtures/upcoming?days=${days}`)
  return response.data
}

// Get single fixture by ID
export async function getFixture(id: number): Promise<Fixture> {
  const response = await apiClient.get<Fixture>(`/api/v1/fixtures/${id}`)
  return response.data
}
