import { IconActivity, IconAlertCircle, IconCheck, IconClock } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useNotifications } from '@/hooks/useNotifications'
import { cn } from '@/lib/utils'

export function NotificationHistory() {
  const { data, isLoading, error } = useNotifications()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }, (_, index) => (
          <Skeleton key={`skeleton-${index}`} className="h-24 w-full rounded-2xl opacity-20" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-destructive/20 bg-destructive/5">
        <CardContent className="p-8 text-center text-destructive">
          <IconAlertCircle className="h-10 w-10 mx-auto mb-4 opacity-50" />
          <p className="font-bold">Failed to load notification history</p>
        </CardContent>
      </Card>
    )
  }

  const notifications = data?.items || []

  if (notifications.length === 0) {
    return (
      <Card className="border-white/5 bg-white/2">
        <CardContent className="p-12 text-center text-muted-foreground">
          <IconActivity className="h-12 w-12 mx-auto mb-4 opacity-10" />
          <p className="font-medium">No signals detected yet.</p>
          <p className="text-xs mt-1 opacity-50">Your filters will trigger notifications here once matches are found.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {notifications.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <Card className="group overflow-hidden border-white/5 hover:border-primary/20 bg-white/2 transition-all">
            <CardContent className="p-5 flex items-center justify-between gap-6">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className={cn(
                  'h-10 w-10 rounded-xl flex items-center justify-center shrink-0 border border-white/5',
                  item.notification_sent ? 'bg-emerald-500/10 text-emerald-500' : 'bg-orange-500/10 text-orange-500',
                )}
                >
                  {item.notification_sent ? <IconCheck className="h-5 w-5" /> : <IconClock className="h-5 w-5" />}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-black uppercase tracking-widest text-primary/80">{item.filter_name}</span>
                    <span className="text-[10px] text-muted-foreground opacity-40">•</span>
                    <span className="text-[10px] font-bold text-muted-foreground opacity-60">
                      {new Date(item.matched_at).toLocaleString()}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm truncate">
                    {item.home_team}
                    {' '}
                    vs
                    {item.away_team}
                  </h4>
                  <p className="text-[11px] text-muted-foreground font-medium opacity-60 truncate">
                    {item.league_name}
                  </p>
                </div>
              </div>

              <div className="flex flex-col items-end gap-2">
                <Badge
                  variant="outline"
                  className={cn(
                    'rounded-lg text-[10px] font-black uppercase tracking-widest px-2 py-0.5 border-white/10',
                    item.bet_result === 'win' && 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
                    item.bet_result === 'loss' && 'bg-destructive/10 text-destructive border-destructive/20',
                    item.bet_result === 'pending' && 'bg-primary/10 text-primary border-primary/20',
                  )}
                >
                  {item.bet_result}
                </Badge>
                {!item.notification_sent && item.notification_error && (
                  <span className="text-[10px] text-destructive font-bold truncate max-w-[120px]">
                    Error:
                    {' '}
                    {item.notification_error}
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
