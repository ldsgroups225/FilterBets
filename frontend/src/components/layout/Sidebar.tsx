import {
  IconActivity,
  IconCalendar,
  IconChevronLeft,
  IconFilter,
  IconLayoutDashboard,
  IconLogout,
  IconSettings,
  IconUser,
} from '@tabler/icons-react'
import { motion } from 'motion/react'
import { useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
  isMobileOpen: boolean
  onMobileClose: () => void
}

const navItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: IconLayoutDashboard,
  },
  {
    title: 'Fixtures',
    href: '/fixtures',
    icon: IconCalendar,
  },
  {
    title: 'Filters',
    href: '/filters',
    icon: IconFilter,
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: IconSettings,
  },
]

export function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileClose }: SidebarProps) {
  const location = useLocation()
  const { user, logout } = useAuth()
  const showLabels = !isCollapsed || isMobileOpen

  // Close mobile menu on route change
  useEffect(() => {
    if (isMobileOpen) {
      onMobileClose()
    }
  }, [location.pathname, isMobileOpen, onMobileClose])

  return (
    <>
      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/40 backdrop-blur-md md:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen glass-dark border-r border-secondary/50 transition-all duration-500 ease-in-out flex flex-col',
          // Mobile state
          isMobileOpen ? 'translate-x-0 w-64 block' : '-translate-x-full md:translate-x-0',
          // Desktop state
          'hidden md:flex',
          isCollapsed ? 'md:w-20' : 'md:w-64',
        )}
      >
        {/* Branding Header */}
        <div className={cn(
          'h-16 flex items-center border-b border-secondary/50 shrink-0',
          showLabels ? 'px-6' : 'justify-center px-0',
        )}
        >
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center">
              <div className="absolute inset-0 bg-primary/20 blur-md rounded-full" />
              <IconActivity className="relative h-6 w-6 text-primary animate-pulse" />
            </div>
            {showLabels && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="font-bold text-lg tracking-tight text-glow whitespace-nowrap"
              >
                FilterBets
              </motion.span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-4 px-3 custom-scrollbar">
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href

              return (
                <NavLink
                  key={item.href}
                  to={item.href}
                  className={({ isActive }) =>
                    cn(
                      'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-all duration-300',
                      isActive
                        ? 'bg-primary/15 text-primary shadow-[inset_0_0_12px_rgba(var(--primary),0.05)]'
                        : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground',
                      !showLabels && 'justify-center px-0',
                    )}
                >
                  <Icon className={cn(
                    'h-5 w-5 transition-transform duration-300 group-hover:scale-110',
                    isActive && 'drop-shadow-[0_0_8px_rgba(var(--primary),0.5)]',
                  )}
                  />
                  {showLabels && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="whitespace-nowrap"
                    >
                      {item.title}
                    </motion.span>
                  )}

                  {isActive && !isCollapsed && !isMobileOpen && (
                    <motion.div
                      layoutId="sidebar-indicator"
                      className="absolute left-0 w-1 h-6 bg-primary rounded-r-full shadow-[0_0_12px_rgba(var(--primary),0.4)]"
                    />
                  )}
                </NavLink>
              )
            })}
          </nav>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-secondary/50 space-y-4 shrink-0 bg-black/10">
          {/* Theme Toggle */}
          <div className={cn('flex items-center', showLabels ? 'justify-between' : 'justify-center')}>
            {showLabels && <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Theme</span>}
            <div className={cn(!showLabels && 'scale-90')}>
              <ThemeToggle />
            </div>
          </div>

          {/* User Profile */}
          {showLabels
            ? (
                <div className="p-3 rounded-xl bg-secondary/50 border border-secondary/50 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-3 min-w-0 overflow-hidden">
                    <div className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0">
                      <IconUser className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold truncate text-foreground" title={user?.email || ''}>
                        {user?.email?.split('@')[0]}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="h-7 w-7 opacity-70 hover:opacity-100 text-destructive hover:bg-destructive/10" onClick={logout} title="Logout">
                    <IconLogout className="h-4 w-4" />
                  </Button>
                </div>
              )
            : (
                <div className="flex flex-col gap-3 items-center">
                  <div className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center" title={user?.email || 'User'}>
                    <IconUser className="h-4 w-4" />
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive/70 hover:text-destructive hover:bg-destructive/10" onClick={logout} title="Logout">
                    <IconLogout className="h-5 w-5" />
                  </Button>
                </div>
              )}

          {/* Collapse Button (Desktop Only) */}
          <div className="hidden md:block pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className={cn(
                'w-full rounded-xl hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-all duration-300',
                !showLabels && 'justify-center',
              )}
            >
              <IconChevronLeft
                className={cn(
                  'h-5 w-5 transition-transform duration-500',
                  isCollapsed && 'rotate-180',
                )}
              />
              {showLabels && <span className="ml-3 font-bold text-xs uppercase tracking-widest">Collapse</span>}
            </Button>
          </div>
        </div>
      </aside>
    </>
  )
}
