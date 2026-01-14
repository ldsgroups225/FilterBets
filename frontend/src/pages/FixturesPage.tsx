import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconCalendar, IconFilter } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { FixturesTable } from '@/components/fixtures/FixturesTable'
import { useFixtures } from '@/hooks/useFixtures'
import type { Fixture, FixtureFilters } from '@/types/fixture'

export function FixturesPage() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<FixtureFilters>({
    page: 1,
    per_page: 20,
  })

  const { data, isLoading, error } = useFixtures(filters)

  // Extract unique leagues from fixtures for filter dropdown
  const leagues = useMemo(() => {
    if (!data?.items) return []
    const uniqueLeagues = new Map<number, string>()
    data.items.forEach((fixture) => {
      uniqueLeagues.set(fixture.league_id, fixture.league_name)
    })
    return Array.from(uniqueLeagues.entries()).map(([id, name]) => ({ id, name }))
  }, [data])

  const handleDateFromChange = (value: string) => {
    setFilters((prev) => ({ ...prev, date_from: value || undefined, page: 1 }))
  }

  const handleDateToChange = (value: string) => {
    setFilters((prev) => ({ ...prev, date_to: value || undefined, page: 1 }))
  }

  const handleLeagueChange = (value: string | null) => {
    setFilters((prev) => ({
      ...prev,
      league_id: !value || value === 'all' ? undefined : parseInt(value),
      page: 1,
    }))
  }

  const handleStatusChange = (value: string | null) => {
    setFilters((prev) => ({
      ...prev,
      status_id: !value || value === 'all' ? undefined : parseInt(value),
      page: 1,
    }))
  }

  const handleClearFilters = () => {
    setFilters({ page: 1, per_page: 20 })
  }

  const handleRowClick = (fixture: Fixture) => {
    navigate(`/fixtures/${fixture.id}`)
  }

  const hasActiveFilters = filters.date_from || filters.date_to || filters.league_id || filters.status_id

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Fixtures</h1>
        <p className="text-muted-foreground">Browse and filter football fixtures</p>
      </div>

      {/* Filters Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <IconFilter className="h-5 w-5" />
                Filters
              </CardTitle>
              <CardDescription>Filter fixtures by date, league, and status</CardDescription>
            </div>
            {hasActiveFilters && (
              <Button variant="outline" size="sm" onClick={handleClearFilters}>
                Clear Filters
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date From */}
            <div className="space-y-2">
              <Label htmlFor="date-from" className="flex items-center gap-2">
                <IconCalendar className="h-4 w-4" />
                Date From
              </Label>
              <Input
                id="date-from"
                type="date"
                value={filters.date_from || ''}
                onChange={(e) => handleDateFromChange(e.target.value)}
              />
            </div>

            {/* Date To */}
            <div className="space-y-2">
              <Label htmlFor="date-to" className="flex items-center gap-2">
                <IconCalendar className="h-4 w-4" />
                Date To
              </Label>
              <Input
                id="date-to"
                type="date"
                value={filters.date_to || ''}
                onChange={(e) => handleDateToChange(e.target.value)}
              />
            </div>

            {/* League Filter */}
            <div className="space-y-2">
              <Label htmlFor="league">League</Label>
              <Select
                value={filters.league_id?.toString() || 'all'}
                onValueChange={handleLeagueChange}
              >
                <SelectTrigger id="league">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Leagues</SelectItem>
                  {leagues.map((league) => (
                    <SelectItem key={league.id} value={league.id.toString()}>
                      {league.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Status Filter */}
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={filters.status_id?.toString() || 'all'}
                onValueChange={handleStatusChange}
              >
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="1">Scheduled</SelectItem>
                  <SelectItem value="2">Live</SelectItem>
                  <SelectItem value="3">Finished</SelectItem>
                  <SelectItem value="4">Postponed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Fixtures Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            {data?.total ? `${data.total} Fixtures` : 'Fixtures'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-destructive">Failed to load fixtures</p>
              <p className="text-sm text-muted-foreground mt-2">
                {error instanceof Error ? error.message : 'Unknown error'}
              </p>
            </div>
          ) : data?.items ? (
            <FixturesTable fixtures={data.items} onRowClick={handleRowClick} />
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No fixtures found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
