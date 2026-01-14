import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconFilter, IconTrash, IconEdit, IconToggleLeft, IconToggleRight } from '@tabler/icons-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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
import type { Filter } from '@/types/filter'

interface FilterCardProps {
  filter: Filter
  onDelete: (id: number) => void
  onToggleActive: (id: number, isActive: boolean) => void
}

export function FilterCard({ filter, onDelete, onToggleActive }: FilterCardProps) {
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const handleDelete = () => {
    onDelete(filter.id)
    setShowDeleteDialog(false)
  }

  const handleToggleActive = () => {
    onToggleActive(filter.id, !filter.is_active)
  }

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <IconFilter className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-lg">{filter.name}</CardTitle>
              </div>
              {filter.description && (
                <CardDescription>{filter.description}</CardDescription>
              )}
            </div>
            <Badge variant={filter.is_active ? 'default' : 'secondary'}>
              {filter.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Filter Info */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Rules:</span>
                <div className="font-medium mt-1">{filter.rules.length} condition(s)</div>
              </div>
              <div>
                <span className="text-muted-foreground">Status:</span>
                <div className="font-medium mt-1">
                  {filter.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2 border-t">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => navigate(`/filters/${filter.id}`)}
              >
                View Details
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/filters/${filter.id}/edit`)}
              >
                <IconEdit className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleToggleActive}
              >
                {filter.is_active ? (
                  <IconToggleRight className="h-4 w-4" />
                ) : (
                  <IconToggleLeft className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDeleteDialog(true)}
              >
                <IconTrash className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Filter</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{filter.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
