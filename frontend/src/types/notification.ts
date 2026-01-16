import type { PaginatedResponse } from './common'

export interface NotificationHistoryItem {
  id: number
  filter_id: number
  filter_name: string
  fixture_id: number
  home_team: string
  away_team: string
  league_name: string
  match_date: string
  matched_at: string
  notification_sent: boolean
  notification_sent_at: string | null
  notification_error: string | null
  bet_result: 'pending' | 'win' | 'loss' | 'push'
}

export type NotificationListResponse = PaginatedResponse<NotificationHistoryItem>
