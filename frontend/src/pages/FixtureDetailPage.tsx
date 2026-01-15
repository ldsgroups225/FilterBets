import { IconArrowLeft, IconCalendar, IconTrophy } from '@tabler/icons-react'
import { format } from 'date-fns'
import { useNavigate, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useFixture } from '@/hooks/useFixtures'

export function FixtureDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const fixtureId = Number.parseInt(id || '0')

  const { data: fixture, isLoading, error } = useFixture(fixtureId)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    )
  }

  if (error || !fixture) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate('/fixtures')}>
          <IconArrowLeft className="mr-2 h-4 w-4" />
          Back to Fixtures
        </Button>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-destructive">Failed to load fixture</p>
              <p className="text-sm text-muted-foreground mt-2">
                {error instanceof Error ? error.message : 'Fixture not found'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const matchDate = new Date(fixture.match_date)
  const statusMap: Record<number, { label: string, variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
    1: { label: 'Scheduled', variant: 'default' },
    2: { label: 'Live', variant: 'destructive' },
    3: { label: 'Finished', variant: 'secondary' },
    4: { label: 'Postponed', variant: 'outline' },
  }
  const status = statusMap[fixture.status_id] || { label: 'Unknown', variant: 'outline' }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/fixtures')}>
          <IconArrowLeft className="mr-2 h-4 w-4" />
          Back to Fixtures
        </Button>
        <Badge variant={status.variant}>{status.label}</Badge>
      </div>

      {/* Match Info Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <IconTrophy className="h-4 w-4" />
            <span>{fixture.league_name}</span>
            <span>•</span>
            <span>{fixture.season}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <IconCalendar className="h-4 w-4" />
            <span>{format(matchDate, 'EEEE, MMMM dd, yyyy')}</span>
            <span>•</span>
            <span>{format(matchDate, 'HH:mm')}</span>
          </div>
        </CardHeader>
        <CardContent>
          {/* Match Score */}
          <div className="flex items-center justify-between py-8">
            {/* Home Team */}
            <div className="flex-1 text-center">
              <h2 className="text-2xl font-bold mb-2">{fixture.home_team_name}</h2>
              {fixture.home_score !== null && (
                <div className="text-5xl font-bold text-primary">{fixture.home_score}</div>
              )}
            </div>

            {/* VS or Score Separator */}
            <div className="px-8">
              {fixture.home_score !== null && fixture.away_score !== null
                ? (
                    <div className="text-2xl font-bold text-muted-foreground">-</div>
                  )
                : (
                    <div className="text-xl font-semibold text-muted-foreground">VS</div>
                  )}
            </div>

            {/* Away Team */}
            <div className="flex-1 text-center">
              <h2 className="text-2xl font-bold mb-2">{fixture.away_team_name}</h2>
              {fixture.away_score !== null && (
                <div className="text-5xl font-bold text-primary">{fixture.away_score}</div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Odds Card */}
      {fixture.home_odds && fixture.draw_odds && fixture.away_odds && (
        <Card>
          <CardHeader>
            <CardTitle>Betting Odds</CardTitle>
            <CardDescription>Pre-match odds for this fixture</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground mb-2">Home Win</div>
                <div className="text-2xl font-bold">{fixture.home_odds.toFixed(2)}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {fixture.home_team_name}
                </div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground mb-2">Draw</div>
                <div className="text-2xl font-bold">{fixture.draw_odds.toFixed(2)}</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground mb-2">Away Win</div>
                <div className="text-2xl font-bold">{fixture.away_odds.toFixed(2)}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {fixture.away_team_name}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Team Statistics Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{fixture.home_team_name}</CardTitle>
            <CardDescription>Home Team Statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              Team statistics will be available in a future update
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{fixture.away_team_name}</CardTitle>
            <CardDescription>Away Team Statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              Team statistics will be available in a future update
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
