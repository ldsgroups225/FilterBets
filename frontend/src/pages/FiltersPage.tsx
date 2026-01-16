import { IconFilter, IconPlus } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { FilterCard } from '@/components/filters/FilterCard'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useDeleteFilter, useFilters, useToggleFilterAlerts, useUpdateFilter } from '@/hooks/useFilters'
import { useTelegramStatus } from '@/hooks/useTelegramStatus'

export function FiltersPage() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useFilters()
  const deleteMutation = useDeleteFilter()
  const updateMutation = useUpdateFilter()
  const toggleAlertsMutation = useToggleFilterAlerts()
  const { data: telegramStatus } = useTelegramStatus()

  const handleDelete = async (id: number) => {
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Filter deleted', { description: 'The strategy has been permanently removed.' })
    }
    catch (err) {
      toast.error('Failed to delete filter')
      console.error('Delete error:', err)
    }
  }

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      await updateMutation.mutateAsync({
        id,
        data: { is_active: isActive },
      })
      toast.success(isActive ? 'Filter activated' : 'Filter paused')
    }
    catch {
      toast.error('Failed to update filter')
    }
  }

  const handleToggleAlerts = async (id: number, enabled: boolean) => {
    if (!telegramStatus?.linked) {
      toast.error('Telegram not linked', {
        description: 'Link your account in Settings to enable notifications.',
        action: { label: 'Settings', onClick: () => navigate('/settings') },
      })
      return
    }

    try {
      await toggleAlertsMutation.mutateAsync({ id, enabled })
      toast.success(enabled ? 'Alerts enabled' : 'Alerts disabled')
    }
    catch {
      toast.error('Failed to toggle alerts')
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-linear-to-r from-foreground to-foreground/50 bg-clip-text text-transparent">
            Filters
          </h1>
          <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground opacity-50 mt-1">
            {data?.meta ? `${data.meta.total_items} ACTIVE STRATEGIES` : 'YOUR STRATEGIES'}
          </h2>
          <p className="text-muted-foreground mt-2 font-medium">
            Manage your automated betting strategies and real-time alerts.
          </p>
        </div>
        <Button
          onClick={() => navigate('/filters/new')}
          className="rounded-xl font-bold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all h-11 px-6"
        >
          <IconPlus className="h-4 w-4 mr-2" />
          Create Filter
        </Button>
      </div>

      {!isLoading && !telegramStatus?.linked && data?.items && data.items.length > 0 && (
        <Alert className="rounded-2xl border-primary/20 bg-primary/5 text-primary">
          <AlertDescription className="flex items-center justify-between font-bold text-xs uppercase tracking-widest">
            <span>Link Telegram to receive real-time push notifications</span>
            <Button variant="link" size="sm" className="h-auto p-0 font-black text-primary hover:text-primary underline" onClick={() => navigate('/settings')}>
              Connect Now
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {isLoading
        ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map(() => (
                <Skeleton key={crypto.randomUUID()} className="h-[280px] w-full rounded-2xl opacity-20" />
              ))}
            </div>
          )
        : error
          ? (
              <Card className="border-destructive/20 bg-destructive/5">
                <CardContent className="py-20 text-center">
                  <p className="text-destructive font-bold text-lg">Failed to load filters</p>
                  <p className="text-sm text-muted-foreground mt-2">{error instanceof Error ? error.message : 'Unknown error'}</p>
                  <Button variant="outline" className="mt-6 rounded-xl border-destructive/20 hover:bg-destructive/10" onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </CardContent>
              </Card>
            )
          : data?.items && data.items.length > 0
            ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {data.items.map(filter => (
                    <motion.div
                      key={filter.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <FilterCard
                        filter={filter}
                        onDelete={handleDelete}
                        onToggleActive={handleToggleActive}
                        onToggleAlerts={handleToggleAlerts}
                      />
                    </motion.div>
                  ))}
                </div>
              )
            : (
                <Card className="border-dashed border-white/10 bg-transparent">
                  <CardContent className="py-32 text-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/5 mx-auto mb-6 text-muted-foreground/30">
                      <IconFilter className="h-8 w-8" />
                    </div>
                    <h3 className="text-xl font-bold">No strategies found</h3>
                    <p className="text-muted-foreground mt-2 max-w-sm mx-auto font-medium">
                      You haven't created any betting filters yet. Start by defining your first automated strategy.
                    </p>
                    <Button onClick={() => navigate('/filters/new')} className="mt-8 rounded-xl px-8 font-bold">
                      Create Your First Filter
                    </Button>
                  </CardContent>
                </Card>
              )}
    </div>
  )
}
