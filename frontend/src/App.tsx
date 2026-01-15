import { Route, Routes } from 'react-router-dom'
import { ErrorBoundary } from './components/layout/ErrorBoundary'
import { Layout } from './components/layout/Layout'
import { ProtectedRoute } from './components/layout/ProtectedRoute'
import { Toaster } from './components/ui/sonner'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { FilterBuilderPage } from './pages/FilterBuilderPage'
import { FilterDetailPage } from './pages/FilterDetailPage'
import { FilterEditPage } from './pages/FilterEditPage'
import { FiltersPage } from './pages/FiltersPage'
import { FixtureDetailPage } from './pages/FixtureDetailPage'
import { FixturesPage } from './pages/FixturesPage'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { RegisterPage } from './pages/RegisterPage'

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
              element={(
                <ProtectedRoute>
                  <Layout>
                    <Home />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/fixtures"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FixturesPage />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/fixtures/:id"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FixtureDetailPage />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/filters"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FiltersPage />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/filters/new"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FilterBuilderPage />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/filters/:id"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FilterDetailPage />
                  </Layout>
                </ProtectedRoute>
              )}
            />
            <Route
              path="/filters/:id/edit"
              element={(
                <ProtectedRoute>
                  <Layout>
                    <FilterEditPage />
                  </Layout>
                </ProtectedRoute>
              )}
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
