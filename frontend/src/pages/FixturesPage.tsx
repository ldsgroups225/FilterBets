import type { FixtureFilters } from '@/types/fixture'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FixturesTable } from '@/components/fixtures/FixturesTable'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
import { useFixtures } from '@/hooks/useFixtures'
import { TIER_STATS } from '@/lib/leagueTiers'

export function FixturesPage() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<FixtureFilters>({
    page: 1,
    per_page: 20,
  })

  const { data, isLoading, error } = useFixtures(filters)

  const leagues = useMemo(() => {
    if (!data?.items)
      return []
    const uniqueLeagues = new Map<number, string>()
    data.items.forEach((fixture) => {
      uniqueLeagues.set(fixture.league_id, fixture.league_name)
    })
    return Array.from(uniqueLeagues.entries()).map(([id, name]) => ({ id, name }))
  }, [data])

  const handleClearFilters = () => {
    setFilters({ page: 1, per_page: 20 })
  }

  const hasActiveFilters = filters.date_from || filters.date_to || filters.league_id || filters.tier || filters.status_id

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-linear-to-r from-foreground to-foreground/50 bg-clip-text text-transparent">
            Fixtures
          </h1>
          <p className="text-muted-foreground mt-2 font-medium">
            Analyze upcoming matches and explore historical performance.
          </p>
          <p className="text-xs text-muted-foreground/60 mt-1">
            {TIER_STATS.tier1Count} Top 5 + {TIER_STATS.tier2Count} Major + Other leagues worldwide
          </p>
        </div>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            className="rounded-xl font-bold text-xs text-primary hover:bg-primary/10"
          >
            Reset Filters
          </Button>
        )}
      </div>

      {/* Filters Card */}
      <Card className="border-white/5 bg-white/2">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <div className="space-y-2.5">
              <Label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">Date From</Label>
              <Input
                type="date"
                value={filters.date_from || ''}
                onChange={e => setFilters(prev => ({ ...prev, date_from: e.target.value || undefined, page: 1 }))}
                className="rounded-xl border-white/10 bg-white/5 focus:ring-primary/20"
              />
            </div>
            <div className="space-y-2.5">
              <Label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">Date To</Label>
              <Input
                type="date"
                value={filters.date_to || ''}
                onChange={e => setFilters(prev => ({ ...prev, date_to: e.target.value || undefined, page: 1 }))}
                className="rounded-xl border-white/10 bg-white/5 focus:ring-primary/20"
              />
            </div>
            <div className="space-y-2.5">
              <Label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">Tier</Label>
              <Select
                value={filters.tier?.toString() || 'all'}
                onValueChange={v => setFilters(prev => ({ ...prev, tier: v === 'all' ? undefined : Number(v) as 1 | 2 | 3, page: 1 }))}
              >
                <SelectTrigger className="rounded-xl border-white/10 bg-white/5">
                  <SelectValue placeholder="All Tiers" />
                </SelectTrigger>
                <SelectContent className="rounded-xl border-white/10 glass-dark">
                  <SelectItem value="all">All Tiers</SelectItem>
                  <SelectItem value="1">
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500" />
                      Top 5 European
                    </span>
                  </SelectItem>
                  <SelectItem value="2">
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500" />
                      Major Leagues
                    </span>
                  </SelectItem>
                  <SelectItem value="3">
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-white/30" />
                      Other Leagues
                    </span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2.5">
              <Label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">League</Label>
              <Select
                value={filters.league_id?.toString() || 'all'}
                onValueChange={v => setFilters(prev => ({ ...prev, league_id: v === 'all' ? undefined : Number(v), page: 1 }))}
              >
                <SelectTrigger className="rounded-xl border-white/10 bg-white/5">
                  <SelectValue placeholder="All Leagues" />
                </SelectTrigger>
                <SelectContent className="rounded-xl border-white/10 glass-dark">
                  <SelectItem value="all">All Leagues</SelectItem>
                  {leagues.map(l => <SelectItem key={l.id} value={l.id.toString()}>{l.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2.5">
              <Label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">Status</Label>
              <Select
                value={filters.status_id?.toString() || 'all'}
                onValueChange={v => setFilters(prev => ({ ...prev, status_id: v === 'all' ? undefined : Number(v), page: 1 }))}
              >
                <SelectTrigger className="rounded-xl border-white/10 bg-white/5">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent className="rounded-xl border-white/10 glass-dark">
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="1">Scheduled</SelectItem>
                  <SelectItem value="2">Live</SelectItem>
                  <SelectItem value="28">Finished</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-2">
          <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground opacity-50">
            {data?.meta ? `${data.meta.total_items} Matches Found` : 'Results'}
          </h2>
        </div>

        <Card className="overflow-hidden border-white/5">
          <CardContent className="p-0">
            {isLoading
              ? (
                <div className="p-8 space-y-4">
                  {Array.from({ length: 6 }).map(() => (
                    <Skeleton key={crypto.randomUUID()} className="h-16 w-full rounded-xl opacity-20" />
                  ))}
                </div>
              )
              : error
                ? (
                  <div className="p-20 text-center">
                    <p className="text-destructive font-bold">Failed to load fixtures</p>
                    <p className="text-xs text-muted-foreground mt-1">Please try again later</p>
                  </div>
                )
                : (
                  <FixturesTable
                    fixtures={data?.items || []}
                    onRowClick={f => navigate(`/fixtures/${f.id}`)}
                  />
                )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
