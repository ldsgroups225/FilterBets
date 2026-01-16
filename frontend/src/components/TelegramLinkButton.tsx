import { IconBrandTelegram, IconLoader2 } from '@tabler/icons-react'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { generateTelegramLink } from '@/services/api/telegram'

export interface TelegramLinkButtonProps {
  onLinkGenerated?: () => void
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
}

export function TelegramLinkButton({
  onLinkGenerated,
  variant = 'default',
  size = 'default',
  className,
}: TelegramLinkButtonProps) {
  const [isRedirecting, setIsRedirecting] = useState(false)

  const linkMutation = useMutation({
    mutationFn: generateTelegramLink,
    onSuccess: (data) => {
      window.open(data.deep_link_url, '_blank')
      setIsRedirecting(true)
      toast.success('Opening Telegram')
      onLinkGenerated?.()
    },
    onError: (error: Error) => {
      toast.error('Failed to generate link', {
        description: (error as any).response?.data?.detail || 'Please try again later.',
      })
    },
  })

  const isLoading = linkMutation.isPending || isRedirecting

  return (
    <Button
      onClick={() => linkMutation.mutate()}
      disabled={isLoading}
      variant={variant}
      size={size}
      className={cn('gap-2.5 font-black uppercase tracking-widest', className)}
    >
      {isLoading
        ? (
            <IconLoader2 className="h-4 w-4 animate-spin" />
          )
        : (
            <IconBrandTelegram className="h-5 w-5" />
          )}
      {isLoading ? 'SECURE LINKING...' : 'CONNECT TELEGRAM'}
    </Button>
  )
}
