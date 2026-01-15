import {
  IconCalendar,
  IconChevronLeft,
  IconFilter,
  IconLayoutDashboard,
  IconX,
} from '@tabler/icons-react'
import { useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
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
]

export function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileClose }: SidebarProps) {
  const location = useLocation()

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
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-14 z-50 h-[calc(100vh-3.5rem)] border-r bg-background transition-all duration-300',
          // Desktop
          'hidden md:block',
          isCollapsed ? 'md:w-16' : 'md:w-64',
          // Mobile
          'md:hidden',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full',
          isMobileOpen && 'block w-64',
        )}
      >
        <div className="flex h-full flex-col">
          {/* Mobile close button */}
          <div className="flex items-center justify-end p-2 md:hidden">
            <Button variant="ghost" size="sm" onClick={onMobileClose}>
              <IconX className="h-4 w-4" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-2">
            {navItems.map(item => (
              <NavLink
                key={item.href}
                to={item.href}
                end={item.href === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    'hover:bg-accent hover:text-accent-foreground',
                    isActive
                      ? 'bg-accent text-accent-foreground'
                      : 'text-muted-foreground',
                    isCollapsed && 'md:justify-center',
                  )}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {(!isCollapsed || isMobileOpen) && <span>{item.title}</span>}
              </NavLink>
            ))}
          </nav>

          {/* Toggle Button (Desktop only) */}
          <div className="hidden border-t p-2 md:block">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className={cn('w-full', isCollapsed && 'justify-center')}
            >
              <IconChevronLeft
                className={cn(
                  'h-4 w-4 transition-transform',
                  isCollapsed && 'rotate-180',
                )}
              />
              {!isCollapsed && <span className="ml-2">Collapse</span>}
            </Button>
          </div>
        </div>
      </aside>
    </>
  )
}
