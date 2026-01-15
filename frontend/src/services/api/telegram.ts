/**
 * Telegram API client functions
 */

import { apiClient } from '../../api/client'

export interface TelegramLinkResponse {
  deep_link_url: string
  expires_in_seconds: number
}

export interface TelegramStatusResponse {
  linked: boolean
  verified: boolean
  chat_id: string | null
}

export interface TelegramUnlinkResponse {
  success: boolean
  message: string
}

/**
 * Generate a Telegram deep link for account linking
 */
export async function generateTelegramLink(): Promise<TelegramLinkResponse> {
  const response = await apiClient.post<TelegramLinkResponse>(
    '/auth/telegram/generate-link',
  )
  return response.data
}

/**
 * Get Telegram link status for current user
 */
export async function getTelegramStatus(): Promise<TelegramStatusResponse> {
  const response = await apiClient.get<TelegramStatusResponse>(
    '/auth/telegram/status',
  )
  return response.data
}

/**
 * Unlink Telegram account from current user
 */
export async function unlinkTelegram(): Promise<TelegramUnlinkResponse> {
  const response = await apiClient.delete<TelegramUnlinkResponse>(
    '/auth/telegram/unlink',
  )
  return response.data
}
