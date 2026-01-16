import type { Fixture } from '@/types/fixture'
import { format } from 'date-fns'
import { useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { CachedImage } from '../ui/cached-image'

interface FixturesTableProps {
  fixtures: Fixture[]
  onRowClick?: (fixture: Fixture) => void
}

export function FixturesTable({ fixtures, onRowClick }: FixturesTableProps) {
  // Group fixtures by league
  const groupedFixtures = useMemo(() => {
    const groups: Record<number, { leagueName: string; leagueLogo?: string | null; fixtures: Fixture[] }> = {}

    fixtures.forEach((fixture) => {
      if (!groups[fixture.league_id]) {
        groups[fixture.league_id] = {
          leagueName: fixture.league_name,
          leagueLogo: fixture.league_logo,
          fixtures: []
        }
      }
      groups[fixture.league_id].fixtures.push(fixture)
    })

    // Sort fixtures within groups by date
    Object.values(groups).forEach(group => {
      group.fixtures.sort((a, b) => new Date(a.match_date).getTime() - new Date(b.match_date).getTime())
    })

    return groups
  }, [fixtures])

  return (
    <div className="space-y-6">
      {Object.values(groupedFixtures).length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 rounded-2xl border border-white/5 bg-white/2">
          <p className="text-muted-foreground font-medium">No fixtures found.</p>
        </div>
      )}

      {Object.values(groupedFixtures).map((group) => (
        <div key={group.leagueName} className="rounded-2xl border border-white/5 bg-[#0A0A0A]/40 overflow-hidden shadow-sm">
          {/* League Header */}
          <div className="flex items-center gap-3 px-4 py-3 bg-white/3 border-b border-white/5 backdrop-blur-sm">
            <CachedImage
              src={group.leagueLogo || undefined}
              alt={group.leagueName}
              className="h-5 w-5 object-contain"
              fallback={<div className="h-5 w-5 rounded-full bg-primary/20 shrink-0" />}
            />
            <h3 className="text-sm font-bold text-foreground/90 tracking-tight">{group.leagueName}</h3>
            <span className="text-[10px] font-medium text-muted-foreground ml-auto bg-white/5 px-2 py-0.5 rounded-full">
              {group.fixtures.length} matches
            </span>
          </div>

          {/* Fixtures List */}
          <div className="divide-y divide-white/5">
            {group.fixtures.map((fixture) => (
              <div
                key={fixture.id}
                onClick={() => onRowClick?.(fixture)}
                className={cn(
                  "grid grid-cols-[auto_1fr_auto] gap-4 items-center px-4 py-3 hover:bg-white/4 transition-all duration-200 group",
                  onRowClick && "cursor-pointer"
                )}
              >
                {/* Time / Status Column */}
                <div className="flex flex-col items-center justify-center w-12 shrink-0 border-r border-white/5 pr-4 mr-0">
                  {fixture.status_id === 2 ? (
                    <span className="text-[10px] font-black text-destructive animate-pulse">LIVE</span>
                  ) : fixture.status_id === 3 || fixture.status_id === 28 ? (
                    <span className="text-[10px] font-black text-primary">FT</span>
                  ) : (
                    <span className="text-xs font-bold text-muted-foreground">{format(new Date(fixture.match_date), 'HH:mm')}</span>
                  )}
                </div>

                {/* Teams Column */}
                <div className="flex flex-col gap-1.5 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <CachedImage
                        src={fixture.home_team_logo || undefined}
                        alt={fixture.home_team_name}
                        className="h-4 w-4 shrink-0"
                        fallback={
                          <div className="h-4 w-4 rounded-full bg-white/5 flex items-center justify-center text-[7px] font-black">{fixture.home_team_name?.[0]}</div>
                        }
                      />
                      <span className={cn("text-xs font-medium truncate", fixture.home_score !== null && fixture.home_score > (fixture.away_score || 0) && "text-primary font-bold")}>
                        {fixture.home_team_name}
                      </span>
                    </div>
                    {fixture.home_score !== null && (
                      <span className="text-xs font-black">{fixture.home_score}</span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <CachedImage
                        src={fixture.away_team_logo || undefined}
                        alt={fixture.away_team_name}
                        className="h-4 w-4 shrink-0"
                        fallback={
                          <div className="h-4 w-4 rounded-full bg-white/5 flex items-center justify-center text-[7px] font-black">{fixture.away_team_name?.[0]}</div>
                        }
                      />
                      <span className={cn("text-xs font-medium truncate", fixture.away_score !== null && fixture.away_score > (fixture.home_score || 0) && "text-primary font-bold")}>
                        {fixture.away_team_name}
                      </span>
                    </div>
                    {fixture.away_score !== null && (
                      <span className="text-xs font-black">{fixture.away_score}</span>
                    )}
                  </div>
                </div>

                {/* Odds / Action Column */}
                <div className="flex items-center gap-2 pl-2 border-l border-white/5">
                  <div className="hidden sm:flex items-center gap-1">
                    <div className="flex flex-col items-center justify-center w-12 h-9 rounded bg-[#1A1A1A] hover:bg-white/10 transition-colors cursor-pointer border border-white/5">
                      <span className="text-[8px] text-muted-foreground/50 font-black mb-0.5">1</span>
                      <span className="text-[10px] font-bold text-foreground">{fixture.home_odds ? fixture.home_odds.toFixed(2) : '-'}</span>
                    </div>
                    <div className="flex flex-col items-center justify-center w-12 h-9 rounded bg-[#1A1A1A] hover:bg-white/10 transition-colors cursor-pointer border border-white/5">
                      <span className="text-[8px] text-muted-foreground/50 font-black mb-0.5">X</span>
                      <span className="text-[10px] font-bold text-foreground">{fixture.draw_odds ? fixture.draw_odds.toFixed(2) : '-'}</span>
                    </div>
                    <div className="flex flex-col items-center justify-center w-12 h-9 rounded bg-[#1A1A1A] hover:bg-white/10 transition-colors cursor-pointer border border-white/5">
                      <span className="text-[8px] text-muted-foreground/50 font-black mb-0.5">2</span>
                      <span className="text-[10px] font-bold text-foreground">{fixture.away_odds ? fixture.away_odds.toFixed(2) : '-'}</span>
                    </div>
                  </div>

                  <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground/50 hover:text-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6" /></svg>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
