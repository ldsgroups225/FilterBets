/**
 * Hook for fetching and polling Telegram link status
 */

import type { TelegramStatusResponse } from '@/services/api/telegram'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getTelegramStatus } from '@/services/api/telegram'

export interface UseTelegramStatusOptions {
  /**
   * Enable polling to check for link status changes
   * Useful after generating a link to detect when user completes linking
   */
  enablePolling?: boolean
  /**
   * Polling interval in milliseconds (default: 3000ms = 3 seconds)
   */
  pollingInterval?: number
}

/**
 * Hook to fetch and optionally poll Telegram link status
 */
export function useTelegramStatus(options: UseTelegramStatusOptions = {}) {
  const { enablePolling = false, pollingInterval = 3000 } = options

  const query = useQuery<TelegramStatusResponse>({
    queryKey: ['telegram', 'status'],
    queryFn: getTelegramStatus,
    refetchInterval: enablePolling ? pollingInterval : false,
    refetchOnWindowFocus: true,
    staleTime: enablePolling ? 0 : 30000, // 30 seconds when not polling
  })

  return query
}

/**
 * Hook to manually invalidate Telegram status cache
 */
export function useInvalidateTelegramStatus() {
  const queryClient = useQueryClient()

  return () => {
    queryClient.invalidateQueries({ queryKey: ['telegram', 'status'] })
  }
}
