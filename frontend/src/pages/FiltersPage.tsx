import { useNavigate } from 'react-router-dom'
import { IconPlus, IconFilter } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { FilterCard } from '@/components/filters/FilterCard'
import { useFilters, useDeleteFilter, useUpdateFilter, useToggleFilterAlerts } from '@/hooks/useFilters'
import { useTelegramStatus } from '@/hooks/useTelegramStatus'
import { toast } from 'sonner'

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
      toast.success('Filter deleted successfully')
    } catch (err) {
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
      toast.success(`Filter ${isActive ? 'activated' : 'deactivated'}`)
    } catch (err) {
      toast.error('Failed to update filter')
      console.error('Update error:', err)
    }
  }

  const handleToggleAlerts = async (id: number, enabled: boolean) => {
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
      await toggleAlertsMutation.mutateAsync({ id, enabled })
      toast.success(`Alerts ${enabled ? 'enabled' : 'disabled'}`)
    } catch (err) {
      toast.error('Failed to toggle alerts')
      console.error('Toggle alerts error:', err)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Filters</h1>
          <p className="text-muted-foreground">
            Manage your betting filter strategies
          </p>
        </div>
        <Button onClick={() => navigate('/filters/new')}>
          <IconPlus className="h-4 w-4 mr-2" />
          Create Filter
        </Button>
      </div>

      {/* Filters List */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-64 w-full" />
          ))}
        </div>
      ) : error ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-destructive">Failed to load filters</p>
              <p className="text-sm text-muted-foreground mt-2">
                {error instanceof Error ? error.message : 'Unknown error'}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : data?.items && data.items.length > 0 ? (
        <>
          {!telegramStatus?.linked && (
            <Alert>
              <AlertDescription>
                Link your Telegram account in{' '}
                <Button
                  variant="link"
                  className="p-0 h-auto font-semibold"
                  onClick={() => navigate('/settings')}
                >
                  Settings
                </Button>{' '}
                to enable notifications for your filters.
              </AlertDescription>
            </Alert>
          )}
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {data.total} filter{data.total !== 1 ? 's' : ''} total
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.items.map((filter) => (
              <FilterCard
                key={filter.id}
                filter={filter}
                onDelete={handleDelete}
                onToggleActive={handleToggleActive}
                onToggleAlerts={handleToggleAlerts}
              />
            ))}
          </div>
        </>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconFilter className="h-5 w-5" />
              No Filters Yet
            </CardTitle>
            <CardDescription>
              Create your first filter to start identifying betting opportunities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                Filters help you automatically scan matches based on your criteria
              </p>
              <Button onClick={() => navigate('/filters/new')}>
                <IconPlus className="h-4 w-4 mr-2" />
                Create Your First Filter
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
