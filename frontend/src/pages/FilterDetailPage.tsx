import type { BacktestRequest, BacktestResponse } from '@/types/backtest'
import {
  IconArrowLeft,
  IconBell,
  IconBellOff,
  IconChartBar,
  IconEdit,
  IconFilter,
  IconToggleLeft,
  IconToggleRight,
  IconTrash,
} from '@tabler/icons-react'
import { format } from 'date-fns'
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
      toast.success('Filter deleted successfully')
      navigate('/filters')
    }
    catch (err) {
      toast.error('Failed to delete filter')
      console.error('Delete error:', err)
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
      toast.success(`Filter ${!filter.is_active ? 'activated' : 'deactivated'}`)
    }
    catch (err) {
      toast.error('Failed to update filter')
      console.error('Update error:', err)
    }
  }

  const handleToggleAlerts = async () => {
    if (!filter)
      return

    if (!telegramStatus?.linked) {
      toast.error('Please link your Telegram account first', {
        description: 'Go to Settings to link your Telegram account and enable notifications.',
        action: {
          label: 'Go to Settings',
          onClick: () => navigate('/settings'),
        },
      })
      return
    }

    try {
      await toggleAlertsMutation.mutateAsync({
        id: filterId,
        enabled: !filter.alerts_enabled,
      })
      toast.success(`Alerts ${!filter.alerts_enabled ? 'enabled' : 'disabled'}`)
    }
    catch (err) {
      toast.error('Failed to toggle alerts')
      console.error('Toggle alerts error:', err)
    }
  }

  const handleRunBacktest = async (data: BacktestRequest) => {
    setIsRunningBacktest(true)
    try {
      const result = await runBacktest(filterId, data)
      setBacktestResult(result)
      toast.success('Backtest completed successfully')
    }
    catch (err) {
      toast.error('Failed to run backtest')
      console.error('Backtest error:', err)
    }
    finally {
      setIsRunningBacktest(false)
    }
  }

  const operatorLabels: Record<string, string> = {
    '=': 'equals',
    '!=': 'not equals',
    '>': 'greater than',
    '<': 'less than',
    '>=': 'greater than or equal',
    '<=': 'less than or equal',
    'in': 'in',
    'between': 'between',
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (error || !filter) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate('/filters')}>
          <IconArrowLeft className="mr-2 h-4 w-4" />
          Back to Filters
        </Button>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-destructive">Failed to load filter</p>
              <p className="text-sm text-muted-foreground mt-2">
                {error instanceof Error ? error.message : 'Filter not found'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/filters')}>
          <IconArrowLeft className="mr-2 h-4 w-4" />
          Back to Filters
        </Button>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleToggleAlerts}
            title={
              !telegramStatus?.linked
                ? 'Link Telegram first to enable alerts'
                : filter.alerts_enabled
                  ? 'Disable alerts'
                  : 'Enable alerts'
            }
            disabled={!telegramStatus?.linked}
          >
            {filter.alerts_enabled
              ? (
                  <>
                    <IconBell className="mr-2 h-4 w-4" />
                    Alerts On
                  </>
                )
              : (
                  <>
                    <IconBellOff className="mr-2 h-4 w-4" />
                    Alerts Off
                  </>
                )}
          </Button>
          <Button variant="outline" onClick={handleToggleActive}>
            {filter.is_active
              ? (
                  <>
                    <IconToggleRight className="mr-2 h-4 w-4" />
                    Deactivate
                  </>
                )
              : (
                  <>
                    <IconToggleLeft className="mr-2 h-4 w-4" />
                    Activate
                  </>
                )}
          </Button>
          <Button variant="outline" onClick={() => navigate(`/filters/${filterId}/edit`)}>
            <IconEdit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button variant="outline" onClick={() => setShowDeleteDialog(true)}>
            <IconTrash className="mr-2 h-4 w-4 text-destructive" />
            Delete
          </Button>
        </div>
      </div>

      {/* Filter Info Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <IconFilter className="h-6 w-6 text-muted-foreground" />
                <CardTitle className="text-2xl">{filter.name}</CardTitle>
              </div>
              {filter.description && <CardDescription>{filter.description}</CardDescription>}
            </div>
            <Badge variant={filter.is_active ? 'default' : 'secondary'} className="text-sm">
              {filter.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Rules Count</span>
              <div className="font-medium mt-1">
                {filter.rules.length}
                {' '}
                conditions
              </div>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Created</span>
              <div className="font-medium mt-1">
                {format(new Date(filter.created_at), 'MMM dd, yyyy')}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filter Rules Card */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Rules</CardTitle>
          <CardDescription>
            {filter.rules.length}
            {' '}
            condition
            {filter.rules.length !== 1 ? 's' : ''}
            {' '}
            must be met
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filter.rules.map((rule, index) => (
              <div
                key={rule.value.toString()}
                className="flex items-center gap-3 p-3 rounded-lg border bg-muted/50"
              >
                <Badge variant="outline" className="font-mono">
                  {index + 1}
                </Badge>
                <div className="flex-1">
                  <div className="font-medium">{rule.field}</div>
                  <div className="text-sm text-muted-foreground">
                    {operatorLabels[rule.operator] || rule.operator}
                    {' '}
                    <span className="font-mono">
                      {Array.isArray(rule.value) ? rule.value.join(', ') : rule.value}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Backtest Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <IconChartBar className="h-5 w-5" />
            Backtest
          </CardTitle>
          <CardDescription>
            Test this filter against historical data to evaluate performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          {backtestResult
            ? (
                <div className="space-y-4">
                  <BacktestResults result={backtestResult} />
                  <Button variant="outline" onClick={() => setBacktestResult(null)}>
                    Run New Backtest
                  </Button>
                </div>
              )
            : (
                <BacktestForm onSubmit={handleRunBacktest} isLoading={isRunningBacktest} />
              )}
        </CardContent>
      </Card>

      {/* Matched Fixtures Section */}
      <Card>
        <CardHeader>
          <CardTitle>Matched Fixtures</CardTitle>
          <CardDescription>
            Fixtures that meet this filter's criteria
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No matched fixtures yet. This feature will show fixtures that trigger this filter.
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Filter</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "
              {filter.name}
              "? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
