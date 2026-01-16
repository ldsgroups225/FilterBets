import { IconActivity, IconLogout, IconMenu2 } from '@tabler/icons-react'
import { motion } from 'motion/react'
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
    <header className="sticky top-0 z-50 w-full glass-dark border-b border-white/5">
      <div className="container flex h-16 items-center">
        {/* Mobile menu button */}
        {isAuthenticated && onMobileMenuToggle && (
          <Button
            variant="ghost"
            size="sm"
            className="mr-2 md:hidden hover:bg-white/5"
            onClick={onMobileMenuToggle}
          >
            <IconMenu2 className="h-5 w-5" />
          </Button>
        )}

        <div className="mr-4 flex items-center">
          <Link to="/" className="mr-8 flex items-center space-x-2 group">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-md rounded-full group-hover:bg-primary/40 transition-colors" />
              <IconActivity className="relative h-6 w-6 text-primary animate-pulse" />
            </div>
            <span className="font-bold text-lg tracking-tight text-glow">FilterBets</span>
          </Link>

          {isAuthenticated && (
            <nav className="hidden lg:flex items-center space-x-8 text-sm font-medium">
              {[
                { label: 'Dashboard', to: '/' },
                { label: 'Fixtures', to: '/fixtures' },
                { label: 'Filters', to: '/filters' },
              ].map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    cn(
                      'relative py-1 transition-all duration-300 hover:text-primary',
                      isActive ? 'text-primary' : 'text-foreground/60',
                    )}
                >
                  {({ isActive }) => (
                    <>
                      {item.label}
                      {isActive && (
                        <motion.div
                          layoutId="nav-underline"
                          className="absolute -bottom-1 left-0 right-0 h-0.5 bg-primary rounded-full shadow-[0_0_8px_rgba(var(--primary),0.5)]"
                        />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          )}
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <ThemeToggle />
          {isAuthenticated
            ? (
                <div className="flex items-center gap-4">
                  <span className="hidden sm:inline text-xs font-medium text-muted-foreground bg-white/5 px-2.5 py-1 rounded-full border border-white/5">
                    {user?.email}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={logout}
                    className="border-white/10 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all font-semibold"
                  >
                    <IconLogout className="h-4 w-4 md:mr-2" />
                    <span className="hidden md:inline">Logout</span>
                  </Button>
                </div>
              )
            : (
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center rounded-lg text-sm font-bold transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-primary/20 bg-primary/10 text-primary shadow-sm hover:bg-primary hover:text-primary-foreground h-9 px-6"
                >
                  Login
                </Link>
              )}
        </div>
      </div>
    </header>
  )
}
