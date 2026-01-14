import { Link } from "react-router-dom"
import { IconActivity, IconLogout } from "@tabler/icons-react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"

export function Header() {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <IconActivity className="h-6 w-6 text-primary" />
            <span className="font-bold">FilterBets</span>
          </Link>
          {isAuthenticated && (
            <nav className="flex items-center space-x-6 text-sm font-medium">
              <Link
                to="/"
                className="transition-colors hover:text-foreground/80 text-foreground/60"
              >
                Dashboard
              </Link>
              <Link
                to="/fixtures"
                className="transition-colors hover:text-foreground/80 text-foreground/60"
              >
                Fixtures
              </Link>
              <Link
                to="/filters"
                className="transition-colors hover:text-foreground/80 text-foreground/60"
              >
                Filters
              </Link>
            </nav>
          )}
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">{user?.email}</span>
              <Button variant="outline" size="sm" onClick={logout}>
                <IconLogout className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          ) : (
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
