import type { NotificationListResponse } from '@/types/notification'
import { apiClient } from '@/api/client'

// Get notification history
export async function getNotificationHistory(page = 1, per_page = 20): Promise<NotificationListResponse> {
  const response = await apiClient.get<NotificationListResponse>(
    `/api/v1/notifications?page=${page}&per_page=${per_page}`,
  )
  return response.data
}
