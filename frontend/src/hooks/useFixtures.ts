import type { FixtureFilters } from '@/types/fixture'
import { useQuery } from '@tanstack/react-query'
import { getFixture, getFixtures, getTodayFixtures, getUpcomingFixtures } from '@/services/fixtures'

export function useFixtures(filters?: FixtureFilters) {
  return useQuery({
    queryKey: ['fixtures', filters],
    queryFn: () => getFixtures(filters),
  })
}

export function useTodayFixtures() {
  return useQuery({
    queryKey: ['fixtures', 'today'],
    queryFn: getTodayFixtures,
  })
}

export function useUpcomingFixtures(days: number = 7) {
  return useQuery({
    queryKey: ['fixtures', 'upcoming', days],
    queryFn: () => getUpcomingFixtures(days),
  })
}

export function useFixture(id: number) {
  return useQuery({
    queryKey: ['fixtures', id],
    queryFn: () => getFixture(id),
    enabled: !!id,
  })
}
