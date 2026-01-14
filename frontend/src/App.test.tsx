import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import App from "./App"

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const renderApp = (initialRoute = "/") => {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe("App", () => {
  it("renders home page by default", () => {
    renderApp()
    expect(screen.getByRole("heading", { name: /Dashboard/i })).toBeInTheDocument()
  })

  it("renders login page on /login route", () => {
    renderApp("/login")
    expect(screen.getByRole("button", { name: /Sign in/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/name@example.com/i)).toBeInTheDocument()
  })

  it("renders 404 page for unknown routes", () => {
    renderApp("/unknown-route")
    expect(screen.getByText(/404/i)).toBeInTheDocument()
  })
})
