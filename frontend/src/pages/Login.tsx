import { IconActivity, IconArrowRight, IconLock, IconMail } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/hooks/useAuth'

export function Login() {
  const { login, isAuthenticated } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  if (isAuthenticated)
    return <Navigate to="/" replace />

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      await login(email, password)
    }
    catch {
      setError('Invalid credentials. Access denied.')
    }
    finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
        className="w-full max-w-[440px] relative z-10"
      >
        <div className="flex flex-col items-center mb-10">
          <motion.div
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="h-16 w-16 bg-primary/20 rounded-2xl flex items-center justify-center border border-primary/30 shadow-xl shadow-primary/20 mb-6"
          >
            <IconActivity className="h-8 w-8 text-primary animate-pulse" />
          </motion.div>
          <h1 className="text-4xl font-black tracking-tight text-glow mb-2">FILTERBETS</h1>
          <p className="text-muted-foreground font-bold uppercase tracking-widest text-[10px] opacity-60">Elite Access Terminal</p>
        </div>

        <Card className="glass-dark border-white/5 shadow-2xl overflow-hidden rounded-[2rem]">
          <CardContent className="p-8 md:p-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2.5">
                <Label htmlFor="email" className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70 ml-1">Terminal ID (Email)</Label>
                <div className="relative group">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground/50 group-focus-within:text-primary transition-colors">
                    <IconMail className="h-4 w-4" />
                  </div>
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                    disabled={isLoading}
                    className="h-12 border-white/10 bg-white/5 pl-11 rounded-xl focus:ring-primary/20 focus:border-primary/50 transition-all font-medium"
                  />
                </div>
              </div>

              <div className="space-y-2.5">
                <div className="flex items-center justify-between px-1">
                  <Label htmlFor="password" title="password" className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-70">Access Code</Label>
                  <Link to="#" className="text-[10px] font-black uppercase text-primary/40 hover:text-primary transition-colors">Emergency Reset</Link>
                </div>
                <div className="relative group">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground/50 group-focus-within:text-primary transition-colors">
                    <IconLock className="h-4 w-4" />
                  </div>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                    disabled={isLoading}
                    className="h-12 border-white/10 bg-white/5 pl-11 rounded-xl focus:ring-primary/20 focus:border-primary/50 transition-all font-medium"
                  />
                </div>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-destructive/10 border border-destructive/20 text-destructive text-[11px] font-bold p-3 rounded-xl flex items-center gap-2"
                >
                  <div className="h-1.5 w-1.5 rounded-full bg-destructive" />
                  {error}
                </motion.div>
              )}

              <Button
                type="submit"
                className="w-full h-12 rounded-xl bg-primary text-primary-foreground font-black uppercase tracking-widest shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-0.5 transition-all group"
                disabled={isLoading}
              >
                {isLoading
                  ? (
                      <span className="flex items-center gap-2">Connecting...</span>
                    )
                  : (
                      <span className="flex items-center gap-2">
                        Initialize Session
                        <IconArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </span>
                    )}
              </Button>
            </form>

            <div className="mt-8 pt-8 border-t border-white/5 text-center">
              <p className="text-muted-foreground text-[11px] font-bold uppercase tracking-widest">
                No credentials?
                <Link to="/register" className="text-primary ml-2 hover:underline">Request Access</Link>
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-center text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground opacity-30 select-none">
          Secure Terminal // Encryption Active
        </div>
      </motion.div>
    </div>
  )
}
