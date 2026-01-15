import { IconActivity, IconLogout, IconMenu2 } from '@tabler/icons-react'
import { Link, NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

interface HeaderProps {
  onMobileMenuToggle?: () => void
}

export function Header({ onMobileMenuToggle }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        {/* Mobile menu button */}
        {isAuthenticated && onMobileMenuToggle && (
          <Button
            variant="ghost"
            size="sm"
            className="mr-2 md:hidden"
            onClick={onMobileMenuToggle}
          >
            <IconMenu2 className="h-5 w-5" />
          </Button>
        )}

        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <IconActivity className="h-6 w-6 text-primary" />
            <span className="font-bold">FilterBets</span>
          </Link>
          <ThemeToggle />
          {isAuthenticated && (
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  cn(
                    'transition-colors hover:text-foreground/80',
                    isActive ? 'text-foreground' : 'text-foreground/60',
                  )}
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/fixtures"
                className={({ isActive }) =>
                  cn(
                    'transition-colors hover:text-foreground/80',
                    isActive ? 'text-foreground' : 'text-foreground/60',
                  )}
              >
                Fixtures
              </NavLink>
              <NavLink
                to="/filters"
                className={({ isActive }) =>
                  cn(
                    'transition-colors hover:text-foreground/80',
                    isActive ? 'text-foreground' : 'text-foreground/60',
                  )}
              >
                Filters
              </NavLink>
            </nav>
          )}
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          {isAuthenticated
            ? (
                <div className="flex items-center gap-2 md:gap-4">
                  <span className="hidden sm:inline text-sm text-muted-foreground">{user?.email}</span>
                  <Button variant="outline" size="sm" onClick={logout}>
                    <IconLogout className="h-4 w-4 md:mr-2" />
                    <span className="hidden md:inline">Logout</span>
                  </Button>
                </div>
              )
            : (
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
                >
                  Login
                </Link>
              )}
        </div>
      </div>
    </header>
  )
}
