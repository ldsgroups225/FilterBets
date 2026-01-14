import { Routes, Route } from "react-router-dom"

import { AuthProvider } from "./contexts/AuthContext"
import { Toaster } from "./components/ui/sonner"
import { Header } from "./components/layout/Header"
import { ProtectedRoute } from "./components/layout/ProtectedRoute"
import { Home } from "./pages/Home"
import { Login } from "./pages/Login"
import { RegisterPage } from "./pages/RegisterPage"
import { NotFound } from "./pages/NotFound"

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-6">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </AuthProvider>
  )
}

export default App
