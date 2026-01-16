import { useQuery } from '@tanstack/react-query'
import { getNotificationHistory } from '@/services/notifications'

export function useNotifications(page = 1, per_page = 20) {
  return useQuery({
    queryKey: ['notifications', page, per_page],
    queryFn: () => getNotificationHistory(page, per_page),
  })
}
