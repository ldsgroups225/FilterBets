import { Routes, Route } from "react-router-dom"

import { AuthProvider } from "./contexts/AuthContext"
import { Toaster } from "./components/ui/sonner"
import { ErrorBoundary } from "./components/layout/ErrorBoundary"
import { Layout } from "./components/layout/Layout"
import { ProtectedRoute } from "./components/layout/ProtectedRoute"
import { Home } from "./pages/Home"
import { Login } from "./pages/Login"
import { RegisterPage } from "./pages/RegisterPage"
import { NotFound } from "./pages/NotFound"

function App() {
  return (
    <ErrorBoundary>
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
                  <div>Fixtures Page (Coming Soon)</div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/filters"
            element={
              <ProtectedRoute>
                <Layout>
                  <div>Filters Page (Coming Soon)</div>
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
        <Toaster />
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
