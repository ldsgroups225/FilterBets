import { getTierBadgeClasses, getTierLabel, type LeagueTier } from '@/lib/leagueTiers'
import { cn } from '@/lib/utils'

interface TierBadgeProps {
  tier: LeagueTier
  size?: 'sm' | 'md'
  className?: string
}

export function TierBadge({ tier, size = 'sm', className }: TierBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center rounded-full border font-bold uppercase tracking-wider',
        getTierBadgeClasses(tier),
        size === 'sm' && 'px-1.5 py-0.5 text-[8px]',
        size === 'md' && 'px-2 py-0.5 text-[10px]',
        className,
      )}
    >
      {getTierLabel(tier)}
    </span>
  )
}
