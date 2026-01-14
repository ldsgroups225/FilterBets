import { format } from 'date-fns'
import {
  IconTrendingUp,
  IconTrendingDown,
  IconChartLine,
  IconCalendar,
} from '@tabler/icons-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { BacktestResponse } from '@/types/backtest'

interface BacktestResultsProps {
  result: BacktestResponse
}

export function BacktestResults({ result }: BacktestResultsProps) {
  const betTypeLabels: Record<string, string> = {
    home_win: 'Home Win',
    away_win: 'Away Win',
    draw: 'Draw',
    over_2_5: 'Over 2.5 Goals',
    under_2_5: 'Under 2.5 Goals',
  }

  const isProfitable = result.total_profit > 0
  const isBreakEven = result.total_profit === 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>Backtest Results</CardTitle>
              <CardDescription>
                {betTypeLabels[result.bet_type]} • Seasons: {result.seasons.join(', ')}
              </CardDescription>
            </div>
            <div className="flex flex-col items-end gap-2">
              <Badge variant={result.cached ? 'secondary' : 'default'}>
                {result.cached ? 'Cached' : 'Fresh'}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {format(new Date(result.run_at), 'MMM dd, yyyy HH:mm')}
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Total Matches</span>
              <div className="text-2xl font-bold">{result.total_matches}</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Win Rate</span>
              <div className="text-2xl font-bold">{result.win_rate.toFixed(1)}%</div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">ROI</span>
              <div
                className={`text-2xl font-bold ${isProfitable ? 'text-green-600' : isBreakEven ? 'text-gray-600' : 'text-red-600'
                  }`}
              >
                {result.roi_percentage > 0 ? '+' : ''}
                {result.roi_percentage.toFixed(1)}%
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Total Profit</span>
              <div
                className={`text-2xl font-bold ${isProfitable ? 'text-green-600' : isBreakEven ? 'text-gray-600' : 'text-red-600'
                  }`}
              >
                {result.total_profit > 0 ? '+' : ''}${result.total_profit.toFixed(2)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Win/Loss/Push Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg bg-green-50 dark:bg-green-950">
              <div className="flex items-center justify-center gap-2 mb-2">
                <IconTrendingUp className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-600">Wins</span>
              </div>
              <div className="text-3xl font-bold">{result.wins}</div>
              <div className="text-sm text-muted-foreground mt-1">
                {((result.wins / result.total_matches) * 100).toFixed(1)}%
              </div>
            </div>

            <div className="text-center p-4 border rounded-lg bg-red-50 dark:bg-red-950">
              <div className="flex items-center justify-center gap-2 mb-2">
                <IconTrendingDown className="h-5 w-5 text-red-600" />
                <span className="text-sm font-medium text-red-600">Losses</span>
              </div>
              <div className="text-3xl font-bold">{result.losses}</div>
              <div className="text-sm text-muted-foreground mt-1">
                {((result.losses / result.total_matches) * 100).toFixed(1)}%
              </div>
            </div>

            <div className="text-center p-4 border rounded-lg bg-gray-50 dark:bg-gray-950">
              <div className="flex items-center justify-center gap-2 mb-2">
                <IconChartLine className="h-5 w-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-600">Pushes</span>
              </div>
              <div className="text-3xl font-bold">{result.pushes}</div>
              <div className="text-sm text-muted-foreground mt-1">
                {((result.pushes / result.total_matches) * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {result.avg_odds && (
            <div className="mt-4 p-4 border rounded-lg">
              <span className="text-sm text-muted-foreground">Average Odds</span>
              <div className="text-xl font-bold">{result.avg_odds.toFixed(2)}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Streak Information */}
      {result.analytics?.streaks && (
        <Card>
          <CardHeader>
            <CardTitle>Streak Analysis</CardTitle>
            <CardDescription>Winning and losing streaks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <span className="text-sm text-muted-foreground">Current Streak</span>
                <div
                  className={`text-2xl font-bold ${result.analytics.streaks.current_streak > 0
                      ? 'text-green-600'
                      : result.analytics.streaks.current_streak < 0
                        ? 'text-red-600'
                        : 'text-gray-600'
                    }`}
                >
                  {result.analytics.streaks.current_streak > 0 ? '+' : ''}
                  {result.analytics.streaks.current_streak}
                </div>
              </div>
              <div className="p-4 border rounded-lg bg-green-50 dark:bg-green-950">
                <span className="text-sm text-muted-foreground">Longest Win Streak</span>
                <div className="text-2xl font-bold text-green-600">
                  {result.analytics.streaks.longest_winning_streak}
                </div>
              </div>
              <div className="p-4 border rounded-lg bg-red-50 dark:bg-red-950">
                <span className="text-sm text-muted-foreground">Longest Loss Streak</span>
                <div className="text-2xl font-bold text-red-600">
                  {result.analytics.streaks.longest_losing_streak}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Drawdown Information */}
      {result.analytics?.drawdown && (
        <Card>
          <CardHeader>
            <CardTitle>Drawdown Analysis</CardTitle>
            <CardDescription>Risk and volatility metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="text-sm text-muted-foreground">Max Drawdown</span>
                <div className="text-xl font-bold text-red-600">
                  ${result.analytics.drawdown.max_drawdown.toFixed(2)}
                </div>
                <div className="text-sm text-muted-foreground">
                  {result.analytics.drawdown.max_drawdown_pct.toFixed(1)}%
                </div>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Current Drawdown</span>
                <div className="text-xl font-bold">
                  ${result.analytics.drawdown.current_drawdown.toFixed(2)}
                </div>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Peak Balance</span>
                <div className="text-xl font-bold text-green-600">
                  ${result.analytics.drawdown.peak_balance.toFixed(2)}
                </div>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Current Balance</span>
                <div className="text-xl font-bold">
                  ${(result.analytics.drawdown.peak_balance - result.analytics.drawdown.current_drawdown).toFixed(2)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Monthly Breakdown */}
      {result.analytics?.monthly_breakdown && result.analytics.monthly_breakdown.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconCalendar className="h-5 w-5" />
              Monthly Breakdown
            </CardTitle>
            <CardDescription>Performance by month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Month</TableHead>
                    <TableHead className="text-right">Matches</TableHead>
                    <TableHead className="text-right">Wins</TableHead>
                    <TableHead className="text-right">Losses</TableHead>
                    <TableHead className="text-right">Win Rate</TableHead>
                    <TableHead className="text-right">Profit</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.analytics.monthly_breakdown.map((month) => (
                    <TableRow key={month.month}>
                      <TableCell className="font-medium">{month.month}</TableCell>
                      <TableCell className="text-right">{month.matches}</TableCell>
                      <TableCell className="text-right text-green-600">{month.wins}</TableCell>
                      <TableCell className="text-right text-red-600">{month.losses}</TableCell>
                      <TableCell className="text-right">{month.win_rate.toFixed(1)}%</TableCell>
                      <TableCell
                        className={`text-right font-medium ${month.profit > 0
                            ? 'text-green-600'
                            : month.profit < 0
                              ? 'text-red-600'
                              : 'text-gray-600'
                          }`}
                      >
                        {month.profit > 0 ? '+' : ''}${month.profit.toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
