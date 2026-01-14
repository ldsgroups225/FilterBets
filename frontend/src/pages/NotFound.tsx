import { Link } from "react-router-dom"
import { IconHome } from "@tabler/icons-react"

import { Button } from "@/components/ui/button"

export function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col items-center justify-center text-center">
      <h1 className="text-9xl font-bold text-muted-foreground/20">404</h1>
      <h2 className="mt-4 text-2xl font-bold">Page not found</h2>
      <p className="mt-2 text-muted-foreground">
        Sorry, we couldn't find the page you're looking for.
      </p>
      <Link to="/">
        <Button className="mt-6">
          <IconHome className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
      </Link>
    </div>
  )
}
