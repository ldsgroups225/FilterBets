import { Link } from "react-router-dom"
import { IconActivity } from "@tabler/icons-react"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <IconActivity className="h-6 w-6 text-primary" />
            <span className="font-bold">FilterBets</span>
          </Link>
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
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
          >
            Login
          </Link>
        </div>
      </div>
    </header>
  )
}
