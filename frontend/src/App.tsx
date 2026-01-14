import { Routes, Route } from "react-router-dom"

import { Header } from "./components/layout/Header"
import { Home } from "./pages/Home"
import { Login } from "./pages/Login"
import { NotFound } from "./pages/NotFound"

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
