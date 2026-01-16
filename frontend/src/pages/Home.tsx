import { IconActivity, IconBell, IconCalendar, IconFilter, IconPlus, IconTrendingUp } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useActiveFiltersCount } from '@/hooks/useFilters'
import { useTodayFixtures } from '@/hooks/useFixtures'
import { cn } from '@/lib/utils'

export function Home() {
  const { data: todayFixtures, isLoading: fixturesLoading } = useTodayFixtures()
  const { data: activeFiltersCount, isLoading: filtersLoading } = useActiveFiltersCount()

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-linear-to-r from-foreground to-foreground/50 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-2 font-medium">
            Welcome back. Here's what's happening today in the markets.
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/fixtures">
            <Button variant="outline" className="rounded-xl font-bold border-white/10 hover:bg-white/5 transition-all">
              <IconCalendar className="h-4 w-4 mr-2" />
              Fixtures
            </Button>
          </Link>
          <Link to="/filters/new">
            <Button className="rounded-xl font-bold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all">
              <IconPlus className="h-4 w-4 mr-2" />
              New Filter
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { // Added missing opening brace here
            title: 'Today\'s Matches',
            value: todayFixtures?.meta.total_items || 0,
            desc: 'Upcoming fixtures',
            icon: IconActivity,
            color: 'text-primary',
            loading: fixturesLoading,
          },
          {
            title: 'Active Filters',
            value: activeFiltersCount || 0,
            desc: 'Running strategies',
            icon: IconFilter,
            color: 'text-cyan-400',
            loading: filtersLoading,
          },
          {
            title: 'Filter Matches',
            value: '--',
            desc: 'Signals detected',
            icon: IconTrendingUp,
            color: 'text-green-400',
          },
          {
            title: 'Notifications',
            value: '--',
            desc: 'Alerts delivered',
            icon: IconBell,
            color: 'text-orange-400',
          },
        ].map(stat => (
          <Card key={stat.title} className="group overflow-hidden">
            <div className={cn('absolute top-0 right-0 w-24 h-24 blur-[60px] rounded-full opacity-20 -mr-12 -mt-12', stat.color.replace('text-', 'bg-'))} />
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-xs uppercase tracking-widest font-bold text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className={cn('h-5 w-5', stat.color)} />
            </CardHeader>
            <CardContent>
              {stat.loading
                ? (
                    <Skeleton className="h-10 w-20 rounded-lg" />
                  )
                : (
                    <>
                      <div className="text-3xl font-black tracking-tighter">{stat.value}</div>
                      <p className="text-xs font-semibold text-muted-foreground mt-1 opacity-70">
                        {stat.desc}
                      </p>
                    </>
                  )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-7">
        {/* Today's Matches List */}
        <div className="lg:col-span-4">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Upcoming Matches</CardTitle>
                  <CardDescription>High probability fixtures detected by your filters</CardDescription>
                </div>
                <Link to="/fixtures">
                  <Button variant="ghost" size="sm" className="text-xs font-bold text-primary hover:text-primary hover:bg-primary/10">
                    View Schedule
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {todayFixtures?.items && todayFixtures.items.length > 0
                ? (
                    <div className="space-y-4">
                      {todayFixtures.items.slice(0, 5).map(fixture => (
                        <motion.div
                          key={fixture.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="group flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-primary/30 hover:bg-white/8 transition-all duration-300"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3">
                              <span className="font-bold truncate text-sm">{fixture.home_team_name}</span>
                              <span className="text-[10px] font-black uppercase text-muted-foreground px-1.5 py-0.5 rounded bg-white/5 tracking-widest">VS</span>
                              <span className="font-bold truncate text-sm">{fixture.away_team_name}</span>
                            </div>
                            <div className="flex items-center gap-2 text-[11px] font-semibold text-muted-foreground mt-2 opacity-60">
                              <span className="truncate">{fixture.league_name}</span>
                              <span className="w-1 h-1 rounded-full bg-muted-foreground" />
                              <span>
                                {new Date(fixture.match_date).toLocaleTimeString('en-US', {
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            {[fixture.home_odds, fixture.draw_odds, fixture.away_odds].map(odds => (
                              <div key={crypto.randomUUID()} className="w-12 py-1.5 text-center text-[11px] font-black rounded-lg bg-background/50 border border-white/5 group-hover:border-primary/10 transition-colors">
                                {odds ? odds.toFixed(2) : '--'}
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )
                : (
                    <div className="h-40 flex flex-col items-center justify-center text-muted-foreground">
                      <IconCalendar className="h-10 w-10 mb-4 opacity-10" />
                      <p className="text-sm font-medium">No matches scheduled for today</p>
                    </div>
                  )}
            </CardContent>
          </Card>
        </div>

        {/* Getting Started / Roadmap */}
        <div className="lg:col-span-3">
          <Card className="h-full bg-linear-to-br from-card to-background">
            <CardHeader>
              <CardTitle>Getting Started</CardTitle>
              <CardDescription>Complete these steps to maximize your edge</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[
                  {
                    step: 1,
                    title: 'Create a Filter',
                    desc: 'Define your betting criteria using odds, team form, and statistics',
                    icon: IconFilter,
                    color: 'bg-primary/20 text-primary',
                  },
                  {
                    step: 2,
                    title: 'Backtest Model',
                    desc: 'Test your filter against historical data to see historical ROI',
                    icon: IconTrendingUp,
                    color: 'bg-green-500/20 text-green-400',
                  },
                  {
                    step: 3,
                    title: 'Enable Alerts',
                    desc: 'Connect Telegram to receive real-time signals',
                    icon: IconBell,
                    color: 'bg-orange-500/20 text-orange-400',
                  },
                ].map(item => (
                  <div key={item.step} className="flex items-start gap-4 p-4 rounded-2xl border border-white/5 hover:bg-white/5 transition-colors">
                    <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl font-bold', item.color)}>
                      <item.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm">{item.title}</h4>
                      <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
