import type { CreateFilterRequest } from '@/types/filter'
import { IconArrowLeft } from '@tabler/icons-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { FilterBuilder } from '@/components/filters/FilterBuilder'
import { Button } from '@/components/ui/button'
import { useCreateFilter } from '@/hooks/useFilters'

export function FilterBuilderPage() {
  const navigate = useNavigate()
  const createMutation = useCreateFilter()

  const handleSubmit = async (data: CreateFilterRequest) => {
    try {
      const filter = await createMutation.mutateAsync(data)
      toast.success('Filter created successfully')
      navigate(`/filters/${filter.id}`)
    }
    catch (err) {
      toast.error('Failed to create filter')
      console.error('Create error:', err)
    }
  }

  const handleCancel = () => {
    navigate('/filters')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={handleCancel}>
            <IconArrowLeft className="mr-2 h-4 w-4" />
            Back to Filters
          </Button>
        </div>
      </div>

      <div>
        <h1 className="text-3xl font-bold">Create Filter</h1>
        <p className="text-muted-foreground">
          Define your betting criteria to automatically scan for matching fixtures
        </p>
      </div>

      {/* Filter Builder Form */}
      <FilterBuilder
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={createMutation.isPending}
      />
    </div>
  )
}
