import { NotificationHistory } from '@/components/NotificationHistory'
import { TelegramStatus } from '@/components/TelegramStatus'

export default function SettingsPage() {
  return (
    <div className="space-y-10 pb-20">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight bg-linear-to-r from-foreground to-foreground/50 bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-muted-foreground mt-2 font-medium">
          Personalize your dashboard and manage your account security.
        </p>
      </div>

      <div className="grid gap-12">
        {/* Telegram Notifications Section */}
        <section>
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground opacity-50">Notifications</h2>
          </div>
          <TelegramStatus enablePolling={false} />
        </section>

        {/* Notification History Section */}
        <section>
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground opacity-50">Signal History</h2>
            <div className="text-[10px] font-bold text-muted-foreground opacity-40 uppercase tracking-widest">Live Feed</div>
          </div>
          <NotificationHistory />
        </section>

        {/* Placeholder for more settings classes */}
        <section className="opacity-40 pointer-events-none">
          <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground opacity-50 mb-4 ml-1">Account Security</h2>
          <div className="p-8 rounded-2xl border border-dashed border-white/10 text-center">
            <p className="text-xs font-bold uppercase tracking-widest opacity-30">Account management coming soon</p>
          </div>
        </section>
      </div>
    </div>
  )
}
