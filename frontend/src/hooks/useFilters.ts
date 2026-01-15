import type { CreateFilterRequest, UpdateFilterRequest } from '@/types/filter'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFilter,
  deleteFilter,
  getActiveFiltersCount,
  getFilter,
  getFilters,
  toggleFilterAlerts,
  updateFilter,
} from '@/services/filters'

export function useFilters() {
  return useQuery({
    queryKey: ['filters'],
    queryFn: getFilters,
  })
}

export function useFilter(id: number) {
  return useQuery({
    queryKey: ['filters', id],
    queryFn: () => getFilter(id),
    enabled: !!id,
  })
}

export function useActiveFiltersCount() {
  return useQuery({
    queryKey: ['filters', 'active-count'],
    queryFn: getActiveFiltersCount,
  })
}

export function useCreateFilter() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateFilterRequest) => createFilter(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['filters'] })
    },
  })
}

export function useUpdateFilter() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number, data: UpdateFilterRequest }) =>
      updateFilter(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['filters'] })
      queryClient.invalidateQueries({ queryKey: ['filters', variables.id] })
    },
  })
}

export function useDeleteFilter() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteFilter(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['filters'] })
    },
  })
}

export function useToggleFilterAlerts() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, enabled }: { id: number, enabled: boolean }) =>
      toggleFilterAlerts(id, enabled),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['filters'] })
      queryClient.invalidateQueries({ queryKey: ['filters', variables.id] })
    },
  })
}
