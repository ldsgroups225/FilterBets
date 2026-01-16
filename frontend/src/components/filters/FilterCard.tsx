import type { Filter } from '@/types/filter'
import { IconBell, IconBellOff, IconEdit, IconFilter, IconToggleLeft, IconToggleRight, IconTrash } from '@tabler/icons-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
import { useTelegramStatus } from '@/hooks/useTelegramStatus'
import { cn } from '@/lib/utils'

interface FilterCardProps {
  filter: Filter
  onDelete: (id: number) => void
  onToggleActive: (id: number, isActive: boolean) => void
  onToggleAlerts?: (id: number, enabled: boolean) => void
}

export function FilterCard({ filter, onDelete, onToggleActive, onToggleAlerts }: FilterCardProps) {
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const { data: telegramStatus } = useTelegramStatus()

  const handleDelete = () => {
    onDelete(filter.id)
    setShowDeleteDialog(false)
  }

  const handleToggleActive = () => {
    onToggleActive(filter.id, !filter.is_active)
  }

  const handleToggleAlerts = () => {
    if (!telegramStatus?.linked)
      return
    onToggleAlerts?.(filter.id, !filter.alerts_enabled)
  }

  return (
    <>
      <Card className="flex flex-col h-full group">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2.5 mb-1.5">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300">
                  <IconFilter className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg truncate font-extrabold tracking-tight">
                  {filter.name}
                </CardTitle>
              </div>
              {filter.description && (
                <CardDescription className="line-clamp-2 min-h-[40px] text-xs">
                  {filter.description}
                </CardDescription>
              )}
            </div>
            <Badge
              variant={filter.is_active ? 'default' : 'secondary'}
              className={cn(
                'rounded-lg font-black text-[10px] uppercase tracking-widest px-2 py-0.5',
                filter.is_active ? 'bg-primary/20 text-primary border-primary/20' : 'bg-white/5 text-muted-foreground border-white/5',
              )}
            >
              {filter.is_active ? 'Active' : 'Paused'}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="pb-6">
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-2xl bg-white/5 border border-white/5">
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground opacity-60">Rules</span>
                <div className="font-black text-sm mt-1 flex items-baseline gap-1">
                  {filter.rules.length}
                  <span className="text-[10px] font-bold opacity-50 uppercase">Conditions</span>
                </div>
              </div>
              <div className="p-3 rounded-2xl bg-white/5 border border-white/5">
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground opacity-60">Alerts</span>
                <div className={cn(
                  'font-black text-sm mt-1 flex items-center gap-1.5',
                  filter.alerts_enabled ? 'text-primary' : 'text-muted-foreground opacity-50',
                )}
                >
                  {filter.alerts_enabled ? <IconBell className="h-4 w-4" /> : <IconBellOff className="h-4 w-4" />}
                  <span className="uppercase text-[10px] tracking-tight">{filter.alerts_enabled ? 'Active' : 'Disabled'}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 rounded-xl font-bold text-xs h-10 border-white/5 hover:bg-white/10"
                onClick={() => navigate(`/filters/${filter.id}`)}
              >
                Analytics
              </Button>
              <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-white/5 border border-white/5">
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    'h-8 w-8 rounded-xl transition-all',
                    filter.alerts_enabled ? 'text-primary bg-primary/10' : 'text-muted-foreground',
                  )}
                  onClick={handleToggleAlerts}
                  disabled={!telegramStatus?.linked}
                >
                  {filter.alerts_enabled ? <IconBell className="h-4 w-4" /> : <IconBellOff className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-xl text-muted-foreground hover:text-foreground"
                  onClick={() => navigate(`/filters/${filter.id}/edit`)}
                >
                  <IconEdit className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    'h-8 w-8 rounded-xl transition-all',
                    filter.is_active ? 'text-primary hover:text-primary' : 'text-muted-foreground hover:text-foreground',
                  )}
                  onClick={handleToggleActive}
                >
                  {filter.is_active ? <IconToggleRight className="h-5 w-5" /> : <IconToggleLeft className="h-5 w-5" />}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-xl text-destructive/60 hover:text-destructive hover:bg-destructive/10"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  <IconTrash className="h-4 w-4" />
                </Button>
              </div>
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
              Are you sure you want to delete "
              {filter.name}
              "? This action cannot be undone.
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
