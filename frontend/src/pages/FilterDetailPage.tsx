import type { BacktestRequest, BacktestResponse } from '@/types/backtest'
import {
  IconArrowLeft,
  IconBell,
  IconBellOff,
  IconChartBar,
  IconEdit,
  IconHistory,
  IconSettings,
  IconToggleLeft,
  IconToggleRight,
  IconTrash,
} from '@tabler/icons-react'
import { format } from 'date-fns'
import { AnimatePresence, motion } from 'motion/react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { BacktestForm } from '@/components/filters/BacktestForm'
import { BacktestResults } from '@/components/filters/BacktestResults'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useDeleteFilter, useFilter, useToggleFilterAlerts, useUpdateFilter } from '@/hooks/useFilters'
import { useTelegramStatus } from '@/hooks/useTelegramStatus'
import { cn } from '@/lib/utils'
import { runBacktest } from '@/services/backtest'

export function FilterDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const filterId = Number.parseInt(id || '0')

  const { data: filter, isLoading, error } = useFilter(filterId)
  const deleteMutation = useDeleteFilter()
  const updateMutation = useUpdateFilter()
  const toggleAlertsMutation = useToggleFilterAlerts()
  const { data: telegramStatus } = useTelegramStatus()

  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null)
  const [isRunningBacktest, setIsRunningBacktest] = useState(false)

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(filterId)
      toast.success('Strategy deleted')
      navigate('/filters')
    }
    catch {
      toast.error('Failed to delete strategy')
    }
    setShowDeleteDialog(false)
  }

  const handleToggleActive = async () => {
    if (!filter)
      return
    try {
      await updateMutation.mutateAsync({
        id: filterId,
        data: { is_active: !filter.is_active },
      })
      toast.success(!filter.is_active ? 'Strategy activated' : 'Strategy paused')
    }
    catch {
      toast.error('Failed to update strategy')
    }
  }

  const handleToggleAlerts = async () => {
    if (!filter)
      return
    if (!telegramStatus?.linked) {
      toast.error('Telegram not linked', {
        description: 'Connect your account in Settings.',
        action: { label: 'Settings', onClick: () => navigate('/settings') },
      })
      return
    }
    try {
      await toggleAlertsMutation.mutateAsync({ id: filterId, enabled: !filter.alerts_enabled })
      toast.success(!filter.alerts_enabled ? 'Alerts enabled' : 'Alerts disabled')
    }
    catch {
      toast.error('Failed to toggle alerts')
    }
  }

  const handleRunBacktest = async (data: BacktestRequest) => {
    setIsRunningBacktest(true)
    try {
      const result = await runBacktest(filterId, data)
      setBacktestResult(result)
      toast.success('Analysis complete')
    }
    catch {
      toast.error('Backtest failed')
    }
    finally {
      setIsRunningBacktest(false)
    }
  }

  const operatorLabels: Record<string, string> = {
    '=': 'is equal to',
    '!=': 'is not equal to',
    '>': 'is greater than',
    '<': 'is less than',
    '>=': 'is at least',
    '<=': 'is at most',
    'in': 'is within',
    'between': 'is between',
  }

  if (isLoading) {
    return (
      <div className="space-y-8 animate-pulse">
        <Skeleton className="h-10 w-48 rounded-xl" />
        <Skeleton className="h-[300px] w-full rounded-2xl" />
        <Skeleton className="h-[200px] w-full rounded-2xl" />
      </div>
    )
  }

  if (error || !filter) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate('/filters')} className="rounded-xl font-bold">
          <IconArrowLeft className="mr-2 h-4 w-4" />
          Back to Strategies
        </Button>
        <Card className="border-destructive/20 bg-destructive/5 py-20 text-center">
          <p className="text-destructive font-bold">Strategy not found</p>
          <Button variant="outline" className="mt-4 rounded-xl" onClick={() => navigate('/filters')}>Retry</Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/filters')} className="rounded-xl h-10 w-10 hover:bg-white/5">
            <IconArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-black tracking-tight text-glow">{filter.name}</h1>
            <p className="text-muted-foreground text-sm font-medium opacity-60">Strategy Analytics & Controls</p>
          </div>
        </div>

        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-white/5 border border-white/5">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleToggleAlerts}
            className={cn(
              'rounded-xl font-bold text-[10px] uppercase tracking-widest h-9 px-4 transition-all',
              filter.alerts_enabled ? 'text-primary bg-primary/10' : 'text-muted-foreground',
            )}
            disabled={!telegramStatus?.linked}
          >
            {filter.alerts_enabled ? <IconBell className="mr-2 h-3.5 w-3.5" /> : <IconBellOff className="mr-2 h-3.5 w-3.5" />}
            Alerts
            {' '}
            {filter.alerts_enabled ? 'Active' : 'Muted'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleToggleActive}
            className={cn(
              'rounded-xl font-bold text-[10px] uppercase tracking-widest h-9 px-4 transition-all',
              filter.is_active ? 'text-primary' : 'text-muted-foreground',
            )}
          >
            {filter.is_active ? <IconToggleRight className="mr-2 h-4 w-4" /> : <IconToggleLeft className="mr-2 h-4 w-4" />}
            {filter.is_active ? 'Running' : 'Paused'}
          </Button>
          <div className="w-px h-6 bg-white/10 mx-1" />
          <Button variant="ghost" size="icon" className="h-9 w-9 rounded-xl" onClick={() => navigate(`/filters/${filterId}/edit`)}>
            <IconEdit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-9 w-9 rounded-xl text-destructive/60 hover:text-destructive hover:bg-destructive/10" onClick={() => setShowDeleteDialog(true)}>
            <IconTrash className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Strategy Definition */}
          <Card className="border-white/5 bg-white/2">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground opacity-50 flex items-center gap-2">
                  <IconSettings className="h-4 w-4" />
                  Definition
                </CardTitle>
                <Badge className="bg-primary/20 text-primary border-primary/20 rounded-lg">
                  {filter.rules.length}
                  {' '}
                  Rules
                </Badge>
              </div>
              {filter.description && <CardDescription className="text-sm font-medium italic mt-2 opacity-80">{filter.description}</CardDescription>}
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                {filter.rules.map((rule, idx) => (
                  <div key={rule.field} className="group p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-primary/20 transition-all flex items-center gap-4">
                    <div className="h-8 w-8 rounded-xl bg-white/5 flex items-center justify-center text-[10px] font-black opacity-30 border border-white/5">
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <span className="text-[10px] font-black uppercase tracking-widest opacity-40">{rule.field}</span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm font-bold text-primary italic">{operatorLabels[rule.operator] || rule.operator}</span>
                        <span className="text-sm font-black bg-white/5 px-2 py-0.5 rounded-lg">
                          {Array.isArray(rule.value) ? rule.value.join(', ') : rule.value}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Analysis Section */}
          <Card className="border-white/5">
            <CardHeader>
              <CardTitle className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground opacity-50 flex items-center gap-2">
                <IconChartBar className="h-4 w-4" />
                Historical backtest
              </CardTitle>
              <CardDescription>Simulate this strategy against archived data sets.</CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatePresence mode="wait">
                {backtestResult
                  ? (
                      <motion.div
                        key="results"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                      >
                        <BacktestResults result={backtestResult} />
                        <Button variant="ghost" onClick={() => setBacktestResult(null)} className="rounded-xl font-bold text-primary hover:bg-primary/10">
                          <IconHistory className="mr-2 h-4 w-4" />
                          Run New Simulation
                        </Button>
                      </motion.div>
                    )
                  : (
                      <motion.div
                        key="form"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      >
                        <BacktestForm onSubmit={handleRunBacktest} isLoading={isRunningBacktest} rulesCount={filter.rules.length} />
                      </motion.div>
                    )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-8">
          <Card className="border-white/5 bg-white/2">
            <CardHeader>
              <CardTitle className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground opacity-50">Strategy metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Created At</span>
                <p className="text-sm font-black mt-1">{format(new Date(filter.created_at), 'MMMM dd, yyyy')}</p>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Total Triggers</span>
                <p className="text-2xl font-black mt-1">
                  0
                  <span className="text-xs opacity-30">matches</span>
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/10">
                <span className="text-[10px] font-black uppercase tracking-widest text-emerald-500 opacity-60">Success Rate</span>
                <p className="text-2xl font-black mt-1 text-emerald-500">N/A</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-dashed border-white/10 bg-transparent">
            <CardHeader>
              <CardTitle className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground opacity-50">Live feed</CardTitle>
            </CardHeader>
            <CardContent className="py-20 text-center">
              <p className="text-xs font-bold uppercase tracking-widest opacity-20 italic">Awaiting first trigger event...</p>
            </CardContent>
          </Card>
        </div>
      </div>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="rounded-4xl border-white/10 glass-dark">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-2xl font-black tracking-tight text-destructive">PURGE STRATEGY?</AlertDialogTitle>
            <AlertDialogDescription className="text-md font-medium">
              You're about to permanently delete
              {' '}
              <strong>{filter.name}</strong>
              . All associated analytics and history will be wiped.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="mt-6 gap-3">
            <AlertDialogCancel className="rounded-xl border-white/10 font-bold">Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="rounded-xl bg-destructive hover:bg-destructive/90 text-white font-bold"
            >
              Confirm Deletion
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
