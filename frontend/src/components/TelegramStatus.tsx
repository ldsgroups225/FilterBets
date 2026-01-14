/**
 * Component showing Telegram link status with unlink option
 */

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { IconCircleCheck, IconCircleX, IconLoader2 } from '@tabler/icons-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { unlinkTelegram } from '@/services/api/telegram';
import { toast } from 'sonner';
import { useTelegramStatus, useInvalidateTelegramStatus } from '@/hooks/useTelegramStatus';
import { TelegramLinkButton } from './TelegramLinkButton';

export interface TelegramStatusProps {
  /**
   * Enable polling to detect link status changes
   */
  enablePolling?: boolean;
}

export function TelegramStatus({ enablePolling = false }: TelegramStatusProps) {
  const { data: status, isLoading } = useTelegramStatus({ enablePolling });
  const invalidateStatus = useInvalidateTelegramStatus();
  const [showUnlinkDialog, setShowUnlinkDialog] = useState(false);

  const unlinkMutation = useMutation({
    mutationFn: unlinkTelegram,
    onSuccess: () => {
      toast.success('Telegram unlinked', {
        description: 'Your Telegram account has been unlinked successfully.',
      });
      invalidateStatus();
      setShowUnlinkDialog(false);
    },
    onError: (error: any) => {
      toast.error('Failed to unlink', {
        description: error.response?.data?.detail || 'Please try again later.',
      });
    },
  });

  const handleUnlink = () => {
    unlinkMutation.mutate();
  };

  const handleLinkGenerated = () => {
    // Start polling after link is generated
    invalidateStatus();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Telegram Notifications</CardTitle>
          <CardDescription>Loading status...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <IconLoader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const isLinked = status?.linked && status?.verified;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Telegram Notifications</CardTitle>
            <CardDescription>
              Receive real-time alerts when matches meet your filter criteria
            </CardDescription>
          </div>
          {isLinked ? (
            <Badge variant="default" className="flex items-center gap-1">
              <IconCircleCheck className="h-3 w-3" />
              Linked
            </Badge>
          ) : (
            <Badge variant="secondary" className="flex items-center gap-1">
              <IconCircleX className="h-3 w-3" />
              Not Linked
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLinked ? (
          <>
            <p className="text-sm text-muted-foreground">
              Your Telegram account is linked. You'll receive notifications when your filters match upcoming matches.
            </p>
            <AlertDialog open={showUnlinkDialog} onOpenChange={setShowUnlinkDialog}>
              <Button variant="outline" size="sm" onClick={() => setShowUnlinkDialog(true)}>
                Unlink Telegram
              </Button>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Unlink Telegram?</AlertDialogTitle>
                  <AlertDialogDescription>
                    You will no longer receive notifications on Telegram. You can link again anytime.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleUnlink}
                    disabled={unlinkMutation.isPending}
                  >
                    {unlinkMutation.isPending && (
                      <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Unlink
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">
              Link your Telegram account to receive instant notifications when matches meet your filter criteria.
            </p>
            <TelegramLinkButton onLinkGenerated={handleLinkGenerated} />
          </>
        )}
      </CardContent>
    </Card>
  );
}
