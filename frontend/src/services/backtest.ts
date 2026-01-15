import type { BacktestRequest, BacktestResponse } from '@/types/backtest'
import { apiClient } from '@/api/client'

// Run backtest for a filter
export async function runBacktest(filterId: number, data: BacktestRequest): Promise<BacktestResponse> {
  const response = await apiClient.post<BacktestResponse>(
    `/api/v1/filters/${filterId}/backtest`,
    data,
  )
  return response.data
}

// Get backtest history for a filter
export async function getBacktestHistory(filterId: number): Promise<BacktestResponse[]> {
  const response = await apiClient.get<BacktestResponse[]>(
    `/api/v1/filters/${filterId}/backtests`,
  )
  return response.data
}
