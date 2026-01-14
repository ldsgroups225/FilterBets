/**
 * Button component for linking Telegram account
 */

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { IconLoader2 } from '@tabler/icons-react';
import { Button } from '@/components/ui/button';
import { generateTelegramLink } from '@/services/api/telegram';
import { toast } from 'sonner';

export interface TelegramLinkButtonProps {
  /**
   * Callback when link is generated and user is redirected
   */
  onLinkGenerated?: () => void;
  /**
   * Button variant
   */
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link';
  /**
   * Button size
   */
  size?: 'default' | 'sm' | 'lg' | 'icon';
  /**
   * Custom class name
   */
  className?: string;
}

export function TelegramLinkButton({
  onLinkGenerated,
  variant = 'default',
  size = 'default',
  className,
}: TelegramLinkButtonProps) {
  const [isRedirecting, setIsRedirecting] = useState(false);

  const linkMutation = useMutation({
    mutationFn: generateTelegramLink,
    onSuccess: (data) => {
      // Open Telegram deep link in new window/tab
      window.open(data.deep_link_url, '_blank');

      setIsRedirecting(true);

      toast.success('Opening Telegram...', {
        description: `Link expires in ${Math.floor(data.expires_in_seconds / 60)} minutes. Complete the linking in Telegram.`,
      });

      onLinkGenerated?.();
    },
    onError: (error: any) => {
      toast.error('Failed to generate link', {
        description: error.response?.data?.detail || 'Please try again later.',
      });
    },
  });

  const handleClick = () => {
    linkMutation.mutate();
  };

  const isLoading = linkMutation.isPending || isRedirecting;

  return (
    <Button
      onClick={handleClick}
      disabled={isLoading}
      variant={variant}
      size={size}
      className={className}
    >
      {isLoading && <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />}
      {isLoading ? 'Opening Telegram...' : 'Link Telegram'}
    </Button>
  );
}
