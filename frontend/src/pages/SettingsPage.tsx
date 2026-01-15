/**
 * Settings page with Telegram integration
 */

import { TelegramStatus } from '@/components/TelegramStatus'

export default function SettingsPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="space-y-6">
          {/* Telegram Notifications Section */}
          <TelegramStatus enablePolling={false} />

          {/* Future sections can be added here */}
          {/* Account Settings, Preferences, etc. */}
        </div>
      </div>
    </div>
  )
}
