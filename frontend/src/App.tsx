import { Routes, Route } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthContext"
import { ThemeProvider } from "./contexts/ThemeContext"
import { Toaster } from "./components/ui/sonner"
import { ErrorBoundary } from "./components/layout/ErrorBoundary"
import { Layout } from "./components/layout/Layout"
import { ProtectedRoute } from "./components/layout/ProtectedRoute"
import { Home } from "./pages/Home"
import { Login } from "./pages/Login"
import { RegisterPage } from "./pages/RegisterPage"
import { FixturesPage } from "./pages/FixturesPage"
import { FixtureDetailPage } from "./pages/FixtureDetailPage"
import { FiltersPage } from "./pages/FiltersPage"
import { FilterBuilderPage } from "./pages/FilterBuilderPage"
import { FilterEditPage } from "./pages/FilterEditPage"
import { NotFound } from "./pages/NotFound"
import { FilterDetailPage } from "./pages/FilterDetailPage"

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes with layout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Home />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/fixtures"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FixturesPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/fixtures/:id"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FixtureDetailPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/filters"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FiltersPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/filters/new"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FilterBuilderPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/filters/:id"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FilterDetailPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/filters/:id/edit"
              element={
                <ProtectedRoute>
                  <Layout>
                    <FilterEditPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          <Toaster />
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
