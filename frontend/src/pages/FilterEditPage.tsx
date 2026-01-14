import { useParams, useNavigate } from 'react-router-dom'
import { IconArrowLeft } from '@tabler/icons-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { FilterBuilder } from '@/components/filters/FilterBuilder'
import { useFilter, useUpdateFilter } from '@/hooks/useFilters'
import { toast } from 'sonner'
import type { CreateFilterRequest } from '@/types/filter'

export function FilterEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const filterId = parseInt(id || '0')

  const { data: filter, isLoading, error } = useFilter(filterId)
  const updateMutation = useUpdateFilter()

  const handleSubmit = async (data: CreateFilterRequest) => {
    try {
      await updateMutation.mutateAsync({
        id: filterId,
        data,
      })
      toast.success('Filter updated successfully')
      navigate(`/filters/${filterId}`)
    } catch (err) {
      toast.error('Failed to update filter')
      console.error('Update error:', err)
    }
  }

  const handleCancel = () => {
    navigate(`/filters/${filterId}`)
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
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load filter</p>
          <p className="text-sm text-muted-foreground mt-2">
            {error instanceof Error ? error.message : 'Filter not found'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={handleCancel}>
            <IconArrowLeft className="mr-2 h-4 w-4" />
            Back to Filter
          </Button>
        </div>
      </div>

      <div>
        <h1 className="text-3xl font-bold">Edit Filter</h1>
        <p className="text-muted-foreground">Update your filter criteria and settings</p>
      </div>

      {/* Filter Builder Form */}
      <FilterBuilder
        initialData={{
          name: filter.name,
          description: filter.description || '',
          bet_type: filter.bet_type,
          rules: filter.rules,
          is_active: filter.is_active,
        }}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={updateMutation.isPending}
      />
    </div>
  )
}
