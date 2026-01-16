import { IconBrandTelegram, IconLoader2, IconShieldCheck } from '@tabler/icons-react'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useInvalidateTelegramStatus, useTelegramStatus } from '@/hooks/useTelegramStatus'
import { cn } from '@/lib/utils'
import { unlinkTelegram } from '@/services/api/telegram'
import { TelegramLinkButton } from './TelegramLinkButton'

export interface TelegramStatusProps {
  enablePolling?: boolean
}

export function TelegramStatus({ enablePolling: initialPolling = false }: TelegramStatusProps) {
  const [isPolling, setIsPolling] = useState(initialPolling)
  const { data: status, isLoading } = useTelegramStatus({ enablePolling: isPolling })
  const invalidateStatus = useInvalidateTelegramStatus()
  const [showUnlinkDialog, setShowUnlinkDialog] = useState(false)

  if (status?.linked && isPolling) {
    setIsPolling(false)
  }

  const unlinkMutation = useMutation({
    mutationFn: unlinkTelegram,
    onSuccess: () => {
      toast.success('Telegram unlinked')
      invalidateStatus()
      setShowUnlinkDialog(false)
    },
    onError: (error: Error) => {
      toast.error('Failed to unlink', {
        description: (error as any).response?.data?.detail || 'Please try again later.',
      })
    },
  })

  // ... (keep isLoading check)

  if (isLoading) {
    return (
      <Card className="border-white/5 bg-white/2 animate-pulse">
        <CardContent className="h-40 flex items-center justify-center">
          <IconLoader2 className="h-6 w-6 animate-spin text-muted-foreground opacity-20" />
        </CardContent>
      </Card>
    )
  }

  const isLinked = status?.linked && status?.verified

  return (
    <Card className="overflow-hidden border-white/5 bg-white/2 group">
      <CardContent className="p-0">
        <div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-white/5">
          {/* ... (keep left side content) */}
          <div className="p-8 flex-1 space-y-6">
            <div className="flex items-start justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <IconBrandTelegram className="h-6 w-6" />
              </div>
              <Badge
                variant={isLinked ? 'default' : 'secondary'}
                className={cn(
                  'rounded-lg font-black text-[10px] uppercase tracking-widest px-2 py-0.5 border-transparent',
                  isLinked ? 'bg-primary/20 text-primary' : 'bg-white/5 text-muted-foreground',
                )}
              >
                {isLinked ? 'CONNECTED' : 'NOT LINKED'}
              </Badge>
            </div>

            <div>
              <h3 className="text-xl font-bold tracking-tight">Telegram Alerts</h3>
              <p className="text-sm text-muted-foreground mt-1 font-medium italic">
                Get notified instantly on your phone when a match hits your filter criteria.
              </p>
            </div>

            <div className="flex items-center gap-4 py-2">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Real-time</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary shadow-[0_0_8px_rgba(var(--primary),0.5)]" />
                <span className="text-[10px] font-black uppercase tracking-widest opacity-60">End-to-End</span>
              </div>
            </div>
          </div>

          <div className="p-8 md:w-80 bg-white/2 flex flex-col justify-center items-center text-center space-y-4">
            {isLinked
              ? (
                  <>
                    <div className="h-12 w-12 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                      <IconShieldCheck className="h-6 w-6" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-bold uppercase tracking-widest text-emerald-500">Security Active</p>
                      <p className="text-sm font-medium opacity-50">Notifications enabled</p>
                    </div>
                    <AlertDialog open={showUnlinkDialog} onOpenChange={setShowUnlinkDialog}>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowUnlinkDialog(true)}
                        className="w-full rounded-xl text-destructive hover:bg-destructive/10 font-bold"
                      >
                        Unlink Account
                      </Button>
                      <AlertDialogContent className="rounded-2xl border-white/10 glass-dark">
                        <AlertDialogHeader>
                          <AlertDialogTitle className="text-2xl font-extrabold uppercase tracking-tight">Pause Notifications?</AlertDialogTitle>
                          <AlertDialogDescription className="font-medium">
                            You'll stop receiving real-time betting alerts on Telegram.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter className="mt-6 gap-3">
                          <AlertDialogCancel className="rounded-xl border-white/10 font-bold">Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => unlinkMutation.mutate()}
                            disabled={unlinkMutation.isPending}
                            className="rounded-xl bg-destructive hover:bg-destructive/90 text-white font-bold"
                          >
                            {unlinkMutation.isPending && <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Disconnect
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </>
                )
              : (
                  <>
                    <div className="space-y-4 w-full">
                      <p className="text-xs font-black uppercase tracking-widest opacity-30 leading-relaxed">
                        Link your account to unlock automated match scanning alerts
                      </p>
                      <TelegramLinkButton
                        variant="default"
                        className="w-full rounded-xl font-bold h-12 shadow-lg shadow-primary/20"
                        onLinkGenerated={() => {
                          invalidateStatus()
                          setIsPolling(true)
                        }}
                      />
                    </div>
                  </>
                )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
