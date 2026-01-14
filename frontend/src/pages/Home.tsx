import { Link } from 'react-router-dom'
import { IconActivity, IconTrendingUp, IconFilter, IconBell, IconPlus, IconCalendar } from "@tabler/icons-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useTodayFixtures } from "@/hooks/useFixtures"
import { useActiveFiltersCount } from "@/hooks/useFilters"

export function Home() {
  const { data: todayFixtures, isLoading: fixturesLoading } = useTodayFixtures()
  const { data: activeFiltersCount, isLoading: filtersLoading } = useActiveFiltersCount()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to FilterBets - Your football betting analytics platform
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/filters/new">
              <IconPlus className="h-4 w-4 mr-2" />
              Create Filter
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/fixtures">
              <IconCalendar className="h-4 w-4 mr-2" />
              View Fixtures
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Matches</CardTitle>
            <IconActivity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {fixturesLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <>
                <div className="text-2xl font-bold">{todayFixtures?.length || 0}</div>
                <p className="text-xs text-muted-foreground">Fixtures available</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Filters</CardTitle>
            <IconFilter className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {filtersLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <>
                <div className="text-2xl font-bold">{activeFiltersCount || 0}</div>
                <p className="text-xs text-muted-foreground">Scanning for matches</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Filter Matches</CardTitle>
            <IconTrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
            <p className="text-xs text-muted-foreground">Matches found today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Notifications</CardTitle>
            <IconBell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
            <p className="text-xs text-muted-foreground">Alerts sent today</p>
          </CardContent>
        </Card>
      </div>

      {/* Today's Matches */}
      {todayFixtures && todayFixtures.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Today's Matches</CardTitle>
            <CardDescription>
              {todayFixtures.length} fixture{todayFixtures.length !== 1 ? 's' : ''} scheduled for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {todayFixtures.slice(0, 5).map((fixture) => (
                <div
                  key={fixture.id}
                  className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{fixture.home_team_name}</span>
                      <span className="text-muted-foreground">vs</span>
                      <span className="font-medium">{fixture.away_team_name}</span>
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {fixture.league_name} • {new Date(fixture.match_date).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                  {fixture.home_odds && fixture.draw_odds && fixture.away_odds && (
                    <div className="flex gap-2 text-sm">
                      <span className="px-2 py-1 rounded bg-muted">{fixture.home_odds.toFixed(2)}</span>
                      <span className="px-2 py-1 rounded bg-muted">{fixture.draw_odds.toFixed(2)}</span>
                      <span className="px-2 py-1 rounded bg-muted">{fixture.away_odds.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              ))}
              {todayFixtures.length > 5 && (
                <Button variant="outline" className="w-full" asChild>
                  <Link to="/fixtures">
                    View all {todayFixtures.length} fixtures
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            Set up your first filter strategy to start receiving match alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
              1
            </div>
            <div>
              <h4 className="font-medium">Create a Filter</h4>
              <p className="text-sm text-muted-foreground">
                Define your betting criteria using odds, team form, and statistics
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
              2
            </div>
            <div>
              <h4 className="font-medium">Backtest Your Strategy</h4>
              <p className="text-sm text-muted-foreground">
                Test your filter against historical data to see potential ROI
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
              3
            </div>
            <div>
              <h4 className="font-medium">Enable Notifications</h4>
              <p className="text-sm text-muted-foreground">
                Connect Telegram to receive alerts when matches meet your criteria
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
