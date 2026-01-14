import { useQuery } from "@tanstack/react-query"
import { IconActivity, IconTrendingUp, IconFilter, IconBell } from "@tabler/icons-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { checkHealth } from "@/api/client"

export function Home() {
  const { data: health, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: checkHealth,
    retry: false,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to FilterBets - Your football betting analytics platform
        </p>
      </div>

      {/* API Status */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">API Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div
              className={`h-2 w-2 rounded-full ${isLoading
                ? "bg-yellow-500"
                : health?.status === "healthy"
                  ? "bg-green-500"
                  : "bg-red-500"
                }`}
            />
            <span className="text-sm">
              {isLoading
                ? "Checking..."
                : health?.status === "healthy"
                  ? `Connected (DB: ${health.database})`
                  : "Disconnected"}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Feature Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Matches</CardTitle>
            <IconActivity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
            <p className="text-xs text-muted-foreground">Fixtures available</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Filters</CardTitle>
            <IconFilter className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
            <p className="text-xs text-muted-foreground">Scanning for matches</p>
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
